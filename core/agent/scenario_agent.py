import logging
import json
from openai import OpenAI
from infra.db_client import DBClient
from graph_db.queries import CypherQueries
from config import Config

logger = logging.getLogger(__name__)

class ScenarioAgent:
    """
    [테스트 시나리오 생성 에이전트]
    변경된 메서드로부터 영향을 받는 엔드포인트를 찾고, 
    LLM을 사용하여 실행 가능한 테스트 시나리오와 페이로드를 생성합니다.
    """
    def __init__(self, db_client: DBClient):
        self.db_client = db_client
        self.client = OpenAI() # 기본적으로 OPENAI_API_KEY 환경변수 사용

    def generate_scenario(self, method_id: str):
        """
        [시나리오 생성 진입점]
        1. 영향 경로 추적
        2. 컨텍스트(소스코드, DTO) 수집
        3. LLM 호출 및 결과 반환
        """
        # 1. 영향 경로 추적 (엔드포인트까지)
        paths = self.db_client.execute_query(
            CypherQueries.GET_PATHS_TO_ENDPOINTS, 
            {"method_id": method_id}
        )
        
        if not paths:
            logger.warning(f"No endpoint found reachable from method_id: {method_id}")
            return {"error": "No reachable endpoint found for this method."}

        results = []
        for row in paths:
            endpoint_info = {
                "url": row["endpoint"],
                "method": row["http_method"],
                "name": row["endpoint_method_name"]
            }
            path = row["path"]
            
            # 2. 경로상의 모든 메서드 컨텍스트 수집
            context = self._collect_path_context(path)
            
            # 3. LLM 시나리오 생성
            scenario = self._call_llm(endpoint_info, context)
            results.append({
                "endpoint": endpoint_info,
                "scenario": scenario
            })

        return results

    def _collect_path_context(self, path):
        """경로상의 노드들로부터 소스코드 및 DTO 구조를 수집합니다."""
        methods_context = []
        dtos_context = {}

        for node in path.nodes:
            if "METHOD" in node.labels:
                method_data = {
                    "name": node.get("name"),
                    "signature": node.get("signature"),
                    "source": node.get("source"),
                    "returnType": node.get("returnType")
                }
                methods_context.append(method_data)
                
                # 해당 메서드의 파라미터 및 DTO 구조 수집
                self._collect_dto_info(node.get("signature"), dtos_context)

        return {
            "methods": methods_context,
            "dtos": dtos_context
        }

    def _collect_dto_info(self, method_signature, dtos_context):
        """메서드의 파라미터가 DTO인 경우 그 내부 FIELD 구조를 재귀적으로 수집합니다."""
        query = """
        MATCH (m:METHOD {signature: $signature})-[:HAS_PARAMETER]->(p:PARAMETER)-[:OF_TYPE]->(t:TYPE)
        OPTIONAL MATCH (t)-[:HAS_FIELD]->(f:FIELD)
        RETURN t.fullName as type_name, f.name as field_name, f.type as field_type
        """
        results = self.db_client.execute_query(query, {"signature": method_signature})
        
        for row in results:
            type_name = row["type_name"]
            if type_name not in dtos_context:
                dtos_context[type_name] = []
            
            if row["field_name"]:
                dtos_context[type_name].append({
                    "name": row["field_name"],
                    "type": row["field_type"]
                })
                
                # 만약 필드 타입도 DTO라면? (간단한 재귀 처리 - 1단계 우선)
                # 실제 구현에서는 더 깊은 탐색이 필요할 수 있음
                # self._collect_type_fields(row["field_type"], dtos_context)

    def _call_llm(self, endpoint, context):
        """OpenAI API를 호출하여 시나리오를 생성합니다."""
        prompt = f"""
당신은 베테랑 QA 엔지니어이자 백엔드 개발자입니다. 
제공된 자바 코드 문맥과 영향도 경로를 바탕으로, 해당 API 엔드포인트를 테스트하기 위한 '자연어 시나리오'와 '요청 페이로드(JSON)'를 생성해 주세요.

[대상 엔드포인트]
- URL: {endpoint['url']}
- HTTP Method: {endpoint['method']}
- Method Name: {endpoint['name']}

[코드 문맥 (영향 경로상의 소스코드)]
{json.dumps(context['methods'], indent=2, ensure_ascii=False)}

[DTO 구조 정보]
{json.dumps(context['dtos'], indent=2, ensure_ascii=False)}

[요구사항]
1. 테스트 시나리오: 사용자의 의도가 포함된 자연어 설명 (예: "새로운 사용자를 등록하기 위해 유효한 정보를 가지고 POST 요청을 보낸다.")
2. 기대 결과: 코드의 비즈니스 로직을 분석하여 예상되는 응답이나 상태 변화 설명.
3. 페이로드: DTO 구조에 맞는 샘플 JSON 데이터.

응답은 반드시 JSON 형식으로 해주세요:
{{
  "scenario": "시나리오 내용",
  "expected_result": "기대 결과 내용",
  "payload": {{ ... }}
}}
"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o", # 또는 gpt-3.5-turbo
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that generates test scenarios in JSON format."},
                    {"role": "user", "content": prompt}
                ],
                response_format={ "type": "json_object" }
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"LLM Call Failed: {e}")
            return {"error": str(e)}
