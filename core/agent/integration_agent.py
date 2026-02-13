import logging
import json
from typing import List, Dict, Any, TypedDict, Annotated
from operator import add

from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field

from infra.db_client import DBClient
from graph_db.queries import CypherQueries

logger = logging.getLogger(__name__)

class IntegrationState(TypedDict):
    """에이전트의 상태를 정의합니다."""
    # 변경된 메서드들의 목록 (ID 또는 Signature)
    source_method_ids: List[str]
    # 엔드포인트별로 그룹화된 영향 경로 및 원인 메서드들
    # { endpoint_url: { "paths": [...], "source_methods": [...] } }
    impact_groups: Dict[str, Any]
    contexts: Dict[str, Any]
    scenarios: Annotated[List[Dict[str, Any]], add]
    errors: List[str]
    next_step: str

class ScenarioOutput(BaseModel):
    """LLM이 생성할 시나리오의 구조입니다."""
    scenario: str = Field(description="테스트 시나리오 설명")
    expected_result: str = Field(description="기대 결과")
    request_payload: str = Field(description="샘플 Request JSON 페이로드를 문자열 형태로 제공")
    response_payload: str = Field(description="샘플 Response JSON 페이로드를 문자열 형태로 제공")

class IntegrationAgent:
    def __init__(self, db_client: DBClient):
        self.db_client = db_client
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.2)
        # strict=False를 명시적으로 주거나, payload를 string으로 받아서 파싱하는 전략 사용
        self.structured_llm = self.llm.with_structured_output(ScenarioOutput)
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(IntegrationState)

        # 노드 추가
        workflow.add_node("planner", self.planner_node)
        workflow.add_node("retriever", self.retriever_node)
        workflow.add_node("generator", self.generator_node)

        # 엣지 정의 (흐름)
        workflow.set_entry_point("planner")
        workflow.add_edge("planner", "retriever")
        workflow.add_edge("retriever", "generator")
        workflow.add_edge("generator", END)

        return workflow.compile()

    def planner_node(self, state: IntegrationState):
        """변경된 메서드들로부터 영향받는 엔드포인트를 그룹화합니다."""
        logger.info(f"Planning for source methods: {state['source_method_ids']}")
        
        impact_groups = {}
        
        for m_id in state['source_method_ids']:
            results = self.db_client.execute_query(
                CypherQueries.GET_PATHS_TO_ENDPOINTS,
                {"method_id": m_id}
            )
            
            for row in results:
                endpoint = row["endpoint"]
                # 엔드포인트가 비어있거나 None인 경우 스킵
                if not endpoint:
                    continue
                    
                if endpoint not in impact_groups:
                    impact_groups[endpoint] = {
                        "url": endpoint,
                        "http_method": row["http_method"],
                        "name": row["endpoint_method_name"],
                        "paths": [],
                        "source_methods": set()
                    }
                
                impact_groups[endpoint]["paths"].append(row["path"])
                impact_groups[endpoint]["source_methods"].add(m_id) # 원인 메서드 추적
            
        if not impact_groups:
            return {"errors": ["No reachable endpoints found from changes."], "next_step": END}
            
        # set을 list로 변환 (JSON 직렬화 및 상태 관리를 위해)
        for ep in impact_groups:
            impact_groups[ep]["source_methods"] = list(impact_groups[ep]["source_methods"])

        return {"impact_groups": impact_groups, "next_step": "retriever"}

    def retriever_node(self, state: IntegrationState):
        """각 엔드포인트 그룹별 컨텍스트를 수집합니다."""
        logger.info("Retrieving contexts for impact groups...")
        contexts = {}
        
        for endpoint, group in state["impact_groups"].items():
            methods_context = []
            dtos_context = {}
            processed_signatures = set()
            
            # 모든 경로상의 노드 정보 수집
            for path in group["paths"]:
                for node in path.nodes:
                    if "METHOD" in node.labels:
                        sig = node.get("signature")
                        if sig not in processed_signatures:
                            methods_context.append({
                                "name": node.get("name"),
                                "signature": sig,
                                "source": node.get("source"),
                                "returnType": node.get("returnType")
                            })
                            processed_signatures.add(sig)
                            self._collect_dto_info(sig, dtos_context)
            
            contexts[endpoint] = {
                "methods": methods_context,
                "dtos": dtos_context,
                "trigger_methods": group["source_methods"]
            }
            
        return {"contexts": contexts, "next_step": "generator"}

    def generator_node(self, state: IntegrationState):
        """수집된 컨텍스트를 기반으로 추적성이 포함된 시나리오를 생성합니다."""
        logger.info("Generating traceability-aware scenarios...")
        scenarios = []
        errors = []
        
        for endpoint, context in state["contexts"].items():
            # 엔드포인트가 비어있거나 None인 경우 스킵
            if not endpoint or endpoint not in state["impact_groups"]:
                continue
                 
            group = state["impact_groups"][endpoint]
            
            # 원인 메서드 이름들을 가져와서 프롬프트에 포함 (추적성 확보)
            trigger_names = [m.split('.')[-1] for m in context['trigger_methods']] # 간단히 클래스명 제외 이름만
            
            prompt = f"""
전략적인 통합 테스트 시나리오를 한국어로 생성해 주세요.
이 테스트는 특히 다음 변경된 메서드들의 영향도를 검증해야 합니다: {', '.join(trigger_names)}

[대상 엔드포인트]
- URL: {endpoint}
- Method: {group['http_method']}
- Name: {group['name']}

[비즈니스 로직 문맥 (영향 경로상의 코드)]
{json.dumps(context['methods'], indent=2, ensure_ascii=False)}

[DTO 데이터 구조]
{json.dumps(context['dtos'], indent=2, ensure_ascii=False)}

[추가 요구사항]
1. 모든 설명과 결과는 **한국어**로 작성해 주세요.
2. `scenario` 필드 ("의도"):
   - 테스트의 전체적인 목적과 변경된 메서드가 미치는 영향을 명확히 설명해 주세요.
   - 텍스트 서술형으로 작성하되, 중요한 부분은 `**굵게**` 표시해 주세요.
3. `expected_result` 필드 ("기대 결과 표"):
   - 이 필드는 반드시 **마크다운 표(Markdown Table)** 형식으로 작성해야 합니다.
   - 표 컬럼 예시: `| 구분 | 상태 코드 | 검증 항목 | 비고 |`
   - 성공 케이스와 다양한 실패 케이스(예외 상황)를 표에 모두 포함해 주세요.
4. `request_payload` 필드: 엔드포인트로 전송할 샘플 Request JSON을 문자열로 작성해 주세요.
5. `response_payload` 필드: 성공 케이스에서 반환될 것으로 예상되는 샘플 Response JSON을 문자열로 작성해 주세요.
"""
            try:
                result = self.structured_llm.invoke(prompt)
                
                # Request Payload JSON 파싱 시도
                request_payload_obj = {}
                try:
                    request_payload_obj = json.loads(result.request_payload)
                except:
                    logger.warning(f"Failed to parse request_payload for {endpoint}, using raw string.")
                    request_payload_obj = {"raw": result.request_payload}

                # Response Payload JSON 파싱 시도
                response_payload_obj = {}
                try:
                    response_payload_obj = json.loads(result.response_payload)
                except:
                    logger.warning(f"Failed to parse response_payload for {endpoint}, using raw string.")
                    response_payload_obj = {"raw": result.response_payload}

                scenarios.append({
                    "endpoint": endpoint,
                    "http_method": group['http_method'],
                    "trigger_methods": context['trigger_methods'],
                    "result": {
                        "scenario": result.scenario,
                        "expected_result": result.expected_result,
                        "request_payload": request_payload_obj,
                        "response_payload": response_payload_obj
                    }
                })
            except Exception as e:
                logger.error(f"Generation failed for {endpoint}: {e}")
                errors.append(f"{endpoint}: {str(e)}")
                
        # 에러가 있으면 상태에 병합 (기존 errors 리스트에 추가됨)
        return {"scenarios": scenarios, "errors": errors}

    def _collect_dto_info(self, method_signature, dtos_context):
        """기존 ScenarioAgent의 로직을 재사용하거나 확장합니다."""
        query = """
        MATCH (m:METHOD {signature: $signature})-[:HAS_PARAMETER]->(p:PARAMETER)-[:OF_TYPE]->(t:TYPE)
        OPTIONAL MATCH (t)-[:HAS_FIELD]->(f:FIELD)
        RETURN t.fullName as type_name, f.name as field_name, f.type as field_type
        """
        results = self.db_client.execute_query(query, {"signature": method_signature})
        
        for row in results:
            type_name = row["type_name"]
            if not type_name: continue
            if type_name not in dtos_context:
                dtos_context[type_name] = []
            
            if row["field_name"]:
                dtos_context[type_name].append({
                    "name": row["field_name"],
                    "type": row["field_type"]
                })

    def run(self, source_method_ids: List[str]):
        """그래프를 실행합니다."""
        initial_state = {
            "source_method_ids": source_method_ids,
            "impact_groups": {},
            "contexts": {},
            "scenarios": [],
            "errors": [],
            "next_step": ""
        }
        return self.graph.invoke(initial_state)
