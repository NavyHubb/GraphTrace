import os
from core.agent.integration_agent import IntegrationAgent
from infra.db_client import DBClient

# DBClient 인스턴스화 (Config 클래스에서 자동으로 설정 로드)
db_client = DBClient()

# IntegrationAgent 인스턴스화
integration_agent = IntegrationAgent(db_client)

# LangGraph Studio에서 참조할 그래프 객체
integration_graph = integration_agent.graph
