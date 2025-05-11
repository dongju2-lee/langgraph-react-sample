#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
DevOps 에이전트를 위한 MCP 클라이언트 (ReAct 패턴 적용, Google Vertex AI 사용)
ReAct 패턴을 사용하여 복잡한 작업을 분할하여 처리할 수 있는 에이전트를 구현합니다.
Google Vertex AI의 Gemini 2.0 Flash 모델을 사용합니다.
"""

import os
import asyncio
import json
from typing import Dict, List, Any, Literal

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from langchain_google_vertexai import ChatVertexAI

from langgraph.graph import StateGraph, END, MessagesState
from langgraph.prebuilt import create_react_agent
from langgraph.types import Command

import datetime
import sys
import re
from dotenv import load_dotenv

from langchain_mcp_adapters.client import MultiServerMCPClient

# 환경 변수 로드
load_dotenv()

# 싱글톤 인스턴스
_agent_instance = None
_mcp_client = None

# MCP 서버 URL 설정
MCP_SERVERS = {
    "grafana": {
        "url": "http://localhost:10001/sse",
        "transport": "sse",
    },
    "argocd": {
        "url": "http://localhost:10002/sse",
        "transport": "sse",
    },
    "k6": {
        "url": "http://localhost:10003/sse",
        "transport": "sse",
    },
    "github": {
        "url": "http://localhost:10004/sse",
        "transport": "sse",
    },
}

# MCP 클라이언트 초기화 함수
async def init_mcp_client():
    """MCP 클라이언트를 초기화합니다."""
    global _mcp_client
    if _mcp_client is None:
        print("MCP 클라이언트 초기화 시작")
        
        try:
            # MCP 클라이언트 생성
            print("MCP 클라이언트 생성 중...")
            client = MultiServerMCPClient(MCP_SERVERS)
            print("MCP 클라이언트 인스턴스 생성 완료")
            
            # MCP 클라이언트 연결
            print("MCP 서버에 연결 시도 중...")
            await client.__aenter__()
            print("MCP 서버 연결 성공")
            
            _mcp_client = client
            print("MCP 클라이언트 초기화 완료")
        except Exception as e:
            print(f"MCP 클라이언트 초기화 중 오류 발생: {str(e)}")
            raise
    
    return _mcp_client

# MCP 도구 가져오기 함수
async def get_tools_with_details() -> List:
    """MCP 도구를 가져오고 상세 정보를 출력합니다."""
    client = await init_mcp_client()
    
    print("MCP 도구 가져오는 중...")
    tools = client.get_tools()
    
    # 도구 정보 출력
    print(f"총 {len(tools)}개의 MCP 도구를 가져왔습니다")
    for i, tool in enumerate(tools, 1):
        try:
            tool_name = getattr(tool, "name", f"Tool-{i}")
            tool_desc = getattr(tool, "description", "설명 없음")
            print(f"  도구 {i}: {tool_name} - {tool_desc}")
        except Exception as e:
            print(f"  도구 {i}의 정보를 가져오는 중 오류: {str(e)}")
    
    return tools

# ReAct 에이전트 생성 함수 (비동기)
async def create_devops_agent():
    """DevOps ReAct 에이전트를 생성합니다."""
    global _agent_instance
    
    # 이미 초기화되어 있으면 반환
    if _agent_instance is not None:
        return _agent_instance
        
    print("DevOps ReAct 에이전트 초기화 시작")
    
    # 모델 설정 가져오기
    model_name = os.environ.get("VERTEX_MODEL", "gemini-2.0-flash")
    print(f"DevOps ReAct 에이전트 LLM 모델: {model_name}")
    
    try:
        # LLM 초기화
        print("LLM 초기화 중...")
        llm = ChatVertexAI(
            model=model_name,
            temperature=0.1,
            max_output_tokens=8190
        )
        print("LLM 초기화 완료")
        
        # MCP 클라이언트 및 도구 가져오기
        print("MCP 도구 로딩 중...")
        tools = await get_tools_with_details()
        print("MCP 도구 로딩 완료")
        
        # ReAct 에이전트 프롬프트
        print("시스템 프롬프트 구성 중...")
        system_prompt = ChatPromptTemplate.from_messages([
            ("system", """당신은 유능한 데브옵스 엔지니어입니다. 사용자의 요청에 따라 시스템 모니터링, 배포 관리, 성능 테스트, 코드 리뷰를 수행합니다.
다음 형식을 사용하여 문제를 해결하세요:

질문: 답변해야 할 입력 질문
생각: 무엇을 해야 할지 항상 먼저 생각하세요
행동: 취할 행동, 사용 가능한 도구 중 하나여야 합니다
행동 입력: 행동에 대한 입력
관찰: 행동의 결과
... (이 생각/행동/행동 입력/관찰 과정은 여러 번 반복될 수 있습니다)
생각: 이제 최종 답변을 알았습니다
최종 답변: 원래 입력 질문에 대한 최종 답변

항상 정확하고 명확한 정보를 제공하세요. 필요한 경우 도구를 사용하여 정보를 조회하고, 
사용자의 질문에 완전하고 상세한 답변을 제공하세요.

필수 참고 사항:
- 도구 호출시 필요한 정보가 부족하면 스스로 판단하지 말고 다시 사용자에게 꼭 물어봐야 합니다.
- 사용자와 한국어로 대화합니다.

모니터링:
- 여러 Grafana 대시보드를 통해 시스템 상태를 모니터링합니다.
- CPU 사용률, 메모리 사용률, Pod 개수 등의 메트릭을 확인할 수 있습니다.
- 프로메테우스, 로키, 템포 등의 데이터소스를 사용하여 정보를 수집합니다.

애플리케이션 배포:
- ArgoCD를 통해 애플리케이션을 배포합니다.
- 유저 서비스, 레스토랑 서비스, 오더 서비스 등의 애플리케이션이 있습니다.
- 배포 후에는 상태를 확인하여 성공 여부를 확인해야 합니다.

성능 테스트:
- k6를 사용하여 서비스의 성능을 테스트합니다.
- 서비스 이름, 가상 사용자 수, 테스트 지속 시간을 지정하여 테스트를 실행합니다.
- 평균 응답 시간, 최고 응답 시간 등의 메트릭을 확인할 수 있습니다.
- 서로 다른 테스트 결과를 비교하여 성능 향상을 확인할 수 있습니다.

코드 리뷰:
- GitHub 풀 리퀘스트(PR)를 통해 코드 변경사항을 검토합니다.
- PR 목록을 확인하고, 필요한 경우 승인할 수 있습니다.
- PR은 기본적으로 열린 상태에서 시작하여 승인 상태로 변경할 수 있습니다."""),
            MessagesPlaceholder(variable_name="messages")
        ])
        print("시스템 프롬프트 설정 완료")
        
        # ReAct 에이전트 생성
        print("ReAct 에이전트 생성 중...")
        _agent_instance = create_react_agent(
            llm, 
            tools, 
            prompt=system_prompt,
            debug=True  # 디버그 모드 활성화
        )
        print("ReAct 에이전트 생성 완료")
        
        print("DevOps ReAct 에이전트 초기화 완료")
    except Exception as e:
        print(f"DevOps ReAct 에이전트 초기화 중 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
        raise
    
    return _agent_instance

# 대화 인터페이스 구현
async def run_conversation_async():
    """대화형 인터페이스 실행 (비동기)"""
    # 에이전트 가져오기
    agent = await create_devops_agent()
    
    # 대화 이력 초기화
    conversation_history = []
    
    print("데브옵스 엔지니어 에이전트에 오신 것을 환영합니다. '종료'를 입력하면 대화가 종료됩니다.")
    
    while True:
        # 사용자 입력 받기
        user_input = input("\n사용자: ")
        
        # 종료 조건 확인
        if user_input.lower() in ['종료', 'exit', 'quit']:
            print("대화를 종료합니다. 감사합니다.")
            break
        
        # 사용자 메시지 추가
        conversation_history.append(HumanMessage(content=user_input))
        
        # 에이전트에 입력 전달
        inputs = {"messages": conversation_history}
        
        try:
            # 에이전트 응답 얻기
            print("\n엔지니어: ", end="")
            result = await agent.ainvoke(inputs)
            
            if "messages" in result and result["messages"]:
                # 마지막 메시지 가져오기
                last_msg = result["messages"][-1]
                print(last_msg.content)
                conversation_history.append(last_msg)
            else:
                print("응답을 생성할 수 없습니다.")
            
        except Exception as e:
            print(f"\n오류가 발생했습니다: {str(e)}")
            import traceback
            traceback.print_exc()

# 단일 쿼리 실행 함수
async def run_single_query_async(query: str):
    """단일 쿼리를 실행하고 응답을 반환합니다."""
    # 에이전트 가져오기
    agent = await create_devops_agent()
    
    print(f"\n쿼리: {query}")
    # 입력 메시지 구성
    inputs = {"messages": [HumanMessage(content=query)]}
    
    # 에이전트 실행
    print("\n에이전트 응답:")
    try:
        result = await agent.ainvoke(inputs)
        
        if "messages" in result and result["messages"]:
            # 마지막 메시지 가져오기
            last_msg = result["messages"][-1]
            print(last_msg.content)
        else:
            print("응답을 생성할 수 없습니다.")
    except Exception as e:
        print(f"\n오류가 발생했습니다: {str(e)}")
        import traceback
        traceback.print_exc()

# 메인 비동기 함수
async def main_async():
    """메인 비동기 함수"""
    print("=" * 50)
    print("Google Vertex AI 기반 DevOps ReAct 에이전트 시작")
    print("=" * 50)
    
    # 모드 선택
    print("\n실행 모드를 선택하세요:")
    print("1: 예제 쿼리 실행")
    print("2: 대화형 인터페이스 실행")
    mode = input("선택 (기본: 2): ").strip() or "2"
    
    if mode == "1":
        # 예제 쿼리 목록
        example_queries = [
            "현재 시스템 상태를 확인해줘",
            "오더 서비스를 배포하고 상태를 확인해줘",
            "주문 서비스에 대해 가상 사용자 50명으로 30초 동안 성능 테스트를 실행해줘",
            "GitHub PR 목록을 보여주고 첫 번째 PR을 승인해줘"
        ]
        
        print("\n사용 가능한 예제 쿼리:")
        for i, query in enumerate(example_queries, 1):
            print(f"{i}: {query}")
        
        choice = input("실행할 쿼리 번호를 선택하세요 (1-4, 또는 0 입력시 직접 입력): ")
        
        try:
            choice_num = int(choice)
            if 1 <= choice_num <= len(example_queries):
                await run_single_query_async(example_queries[choice_num-1])
            elif choice_num == 0:
                custom_query = input("실행할 쿼리를 입력하세요: ")
                await run_single_query_async(custom_query)
            else:
                print("잘못된 선택입니다.")
        except ValueError:
            print("숫자를 입력해주세요.")
    else:
        # 대화형 인터페이스 실행
        await run_conversation_async()

# 메인 함수
def main():
    """메인 함수"""
    # 새 이벤트 루프 생성
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print("\n프로그램이 사용자에 의해 종료되었습니다.")
    except Exception as e:
        print(f"\n오류가 발생했습니다: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 