import sys
import os
from unittest.mock import MagicMock
import tree_sitter_languages

# 프로젝트 루트를 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.analysis.strategies.java import JavaFlowStrategy

def test_reproduction():
    # Mock DB Connector
    mock_connector = MagicMock()
    strategy = JavaFlowStrategy(mock_connector)
    
    # 가상의 Java 소스 코드
    source_code = b"""
    package com.ssafy.algonote.member.service;
    
    public class MemberService {
        public void login(LoginReqDto dto) {
        }
    }
    """
    
    # Tree-sitter 파싱
    parser = tree_sitter_languages.get_parser("java")
    tree = parser.parse(source_code)
    
    # 분석 실행 (파일 경로는 MemberService.java 로 가동)
    file_path = "/path/to/MemberService.java"
    strategy.process(tree, source_code, file_path)
    
    # execute_query 호출 인자 확인
    for call in mock_connector.execute_query.call_args_list:
        query, params = call.args if len(call.args) == 2 else (call.args[0], call.kwargs.get('params', {}))
        if "signature" in params:
            print(f"Generated Signature: {params['signature']}")
        if "full_name" in params:
             print(f"Generated Full Name (Type): {params['full_name']}")

if __name__ == "__main__":
    test_reproduction()
