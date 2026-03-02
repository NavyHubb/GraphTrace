from fastapi import APIRouter, HTTPException, Request
from core.agent.scenario_agent import ScenarioAgent
from core.agent.integration_agent import IntegrationAgent
from core.agent.happy_case_agent import HappyCaseAgent

router = APIRouter(prefix="/agent", tags=["agent"])

@router.get("/scenario/{method_id}")
async def get_test_scenario(method_id: str, request: Request):
    """
    변경된 메서드 정보를 기반으로 자연어 테스트 시나리오와 JSON 페이로드를 생성합니다.
    """
    analyzer = getattr(request.app.state, "analyzer", None)
    if not analyzer:
        raise HTTPException(status_code=503, detail="Analysis Agent not initialized")

    try:
        agent = ScenarioAgent(analyzer.connector)
        scenarios = agent.generate_scenario(method_id)
        return {"scenarios": scenarios}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/integration-scenario/{method_id}")
async def get_integration_test_scenario(method_id: str, request: Request):
    """
    LangGraph 에이전트를 사용하여 특정 메서드 변경에 따른 고도화된 통합 테스트 시나리오를 생성합니다.
    """
    analyzer = getattr(request.app.state, "analyzer", None)
    if not analyzer:
        raise HTTPException(status_code=503, detail="Analysis Agent not initialized")

    try:
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Generating scenario for method: {method_id}")

        agent = IntegrationAgent(analyzer.connector)
        # 단일 메서드 ID를 리스트로 감싸서 전달
        result = agent.run([method_id])
        return {
            "method_id": method_id,
            "scenarios": result.get("scenarios", []),
            "errors": result.get("errors", [])
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.error(f"Error in single scenario generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/integration-scenario/batch/all")
async def get_batch_integration_test_scenarios(request: Request):
    """
    프로젝트 내 모든 변경(MODIFIED, NEW)된 메서드들을 취합하여 일괄 시나리오를 생성합니다.
    """
    analyzer = getattr(request.app.state, "analyzer", None)
    if not analyzer:
        raise HTTPException(status_code=503, detail="Analysis Agent not initialized")

    try:
        # 1. 변경된 메서드들 찾기 (초기 프로젝트 로드 시 NEW가 너무 많아지는 문제를 방지하기 위해 MODIFIED만 우선 대상)
        # 추후 사용자가 옵션으로 NEW/DELETED를 선택할 수 있게 확장 가능
        query = "MATCH (m:METHOD) WHERE m.status = 'MODIFIED' RETURN elementId(m) as id"
        records = analyzer.connector.execute_query(query)
        method_ids = [r["id"] for r in records]

        if not method_ids:
            return {"message": "No modified methods found.", "scenarios": []}

        # 2. 에이전트 실행
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Analyzing {len(method_ids)} modified methods...")
        
        agent = IntegrationAgent(analyzer.connector)
        result = agent.run(method_ids)
        
        return {
            "source_method_count": len(method_ids),
            "scenarios": result.get("scenarios", []),
            "errors": result.get("errors", [])
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.error(f"Error in batch generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/happy-case/batch")
async def get_happy_case_scenarios(request: Request):
    """
    프로젝트 내 모든 변경(MODIFIED)된 메서드들을 취합하여 Happy Case(200 OK) 시나리오를 일괄 생성합니다.
    """
    analyzer = getattr(request.app.state, "analyzer", None)
    if not analyzer:
        raise HTTPException(status_code=503, detail="Analysis Agent not initialized")

    try:
        # 1. 변경된 메서드들 찾기
        query = "MATCH (m:METHOD) WHERE m.status = 'MODIFIED' RETURN elementId(m) as id"
        records = analyzer.connector.execute_query(query)
        method_ids = [r["id"] for r in records]

        if not method_ids:
            return {"message": "No modified methods found.", "scenarios": []}

        # 2. HappyCaseAgent 실행
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Generating happy-case scenarios for {len(method_ids)} methods...")
        
        agent = HappyCaseAgent(analyzer.connector)
        result = agent.run(method_ids)
        
        return {
            "source_method_count": len(method_ids),
            "scenarios": result.get("scenarios", []),
            "errors": result.get("errors", [])
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.error(f"Error in happy-case generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))
