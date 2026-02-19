import logging
import json
from unittest.mock import MagicMock, patch
from typing import List, Dict, Any

# Mocking modules before importing IntegrationAgent
import sys
from types import ModuleType

# Mock DBClient
class MockDBClient:
    def execute_query(self, query, params=None):
        query_str = str(query)
        if "source.endpoint as endpoint" in query_str:
            # GET_PATHS_TO_ENDPOINTS
            return [
                {
                    "endpoint": "/api/test",
                    "http_method": "POST",
                    "endpoint_method_name": "testMethod",
                    "path": MagicMock(nodes=[MagicMock(labels=["METHOD"], get=lambda x: "testSignature" if x=="signature" else ("testName" if x=="name" else None))]),
                    "source_methods": ["test_id"]
                }
            ]
        elif "HAS_PARAMETER" in query_str:
            # _collect_dto_info
            return [
                {
                    "type_name": "TestDTO",
                    "field_name": "id",
                    "field_type": "Long"
                }
            ]
        return []

# Import after mocks might be tricky, let's just patch it in the script
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.agent.integration_agent import IntegrationAgent, ScenarioOutput, ValidatorOutput

def test_loop_logic():
    logging.basicConfig(level=logging.INFO)
    
    mock_db = MockDBClient()
    agent = IntegrationAgent(db_client=mock_db)
    
    mock_scenario = ScenarioOutput(
        scenario="Test Scenario",
        expected_result="| Case | Status |",
        request_payload='{"id": 1}',
        response_payload='{"status": "ok"}'
    )
    
    mock_validator_fail = ValidatorOutput(
        is_valid=False,
        feedback="Please add more details to the scenario.",
        endpoint="/api/test"
    )
    
    mock_validator_success = ValidatorOutput(
        is_valid=True,
        feedback="",
        endpoint="/api/test"
    )
    
    # Replace the actual LLMs with MagicMocks
    agent.structured_llm = MagicMock()
    agent.validator_llm = MagicMock()
    
    agent.structured_llm.invoke.return_value = mock_scenario
    # Return fail first, then success
    agent.validator_llm.invoke.side_effect = [mock_validator_fail, mock_validator_success]
    
    print("Running agent with max_iterations=3...")
    result = agent.run(source_method_ids=["test_id"], max_iterations=3)
    
    print(f"Final Iterations: {result['iterations']}")
    print(f"Impact Groups Found: {len(result['impact_groups'])}")
    print(f"Scenarios Generated: {len(result['scenarios'])}")
    print(f"Validation Results: {len(result['validation_results'])}")
    
    assert result['iterations'] == 2
    assert len(result['validation_results']) >= 1
    assert result['validation_results'][-1]['is_valid'] == True
    print("Loop logic test passed!")

def test_max_iterations():
    mock_db = MockDBClient()
    agent = IntegrationAgent(db_client=mock_db)
    
    mock_scenario = ScenarioOutput(
        scenario="Test Scenario",
        expected_result="| Case | Status |",
        request_payload='{"id": 1}',
        response_payload='{"status": "ok"}'
    )
    
    mock_validator_fail = ValidatorOutput(
        is_valid=False,
        feedback="Persistent error",
        endpoint="/api/test"
    )
    
    agent.structured_llm = MagicMock()
    agent.validator_llm = MagicMock()
    
    agent.structured_llm.invoke.return_value = mock_scenario
    agent.validator_llm.invoke.return_value = mock_validator_fail
    
    print("Running agent with max_iterations=2 (constant fail)...")
    result = agent.run(source_method_ids=["test_id"], max_iterations=2)
    
    print(f"Iterations: {result['iterations']}")
    assert result['iterations'] == 2
    print("Max iterations test passed!")

if __name__ == "__main__":
    try:
        test_loop_logic()
        test_max_iterations()
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
