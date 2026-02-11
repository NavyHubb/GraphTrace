from fastapi import APIRouter, HTTPException, Request
from core.agent.scenario_agent import ScenarioAgent

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
