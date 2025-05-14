#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
스마트홈 에이전트 (Google Vertex AI 사용)
사용자의 요청을 분석하고 어떤 스마트홈 도구를 어떤 순서로 사용할지 계획을 제시합니다.
Google Vertex AI의 Gemini 모델을 사용합니다.
MCP 서버에서 도구 정보를 동적으로 가져와 사용합니다.
"""

import os
import asyncio
import signal
from typing import Dict, List, Any
import contextlib

from langchain_google_vertexai import ChatVertexAI
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from langgraph.graph import StateGraph, END, MessagesState
from langgraph.prebuilt import create_react_agent

# 환경 변수 로드
load_dotenv()

# 싱글톤 인스턴스
_llm_instance = None
_mcp_client = None
_mcp_tools_cache = None

# MCP 서버 URL 설정
MCP_SERVERS = {
    "refrigerator": {
        "url": "http://localhost:8001/sse",
        "transport": "sse",
    },
    "induction": {
        "url": "http://localhost:8002/sse",
        "transport": "sse",
    },
    "microwave": {
        "url": "http://localhost:8003/sse",
        "transport": "sse",
    },
    "mobile": {
        "url": "http://localhost:8004/sse",
        "transport": "sse",
    },
    "cooking": {
        "url": "http://localhost:8005/sse",
        "transport": "sse",
    },
    "personalization": {
        "url": "http://localhost:8006/sse",
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
            if client:
                try:
                    await client.__aexit__(None, None, None)
                except Exception as close_error:
                    print(f"클라이언트 종료 중 오류: {str(close_error)}")
            raise
    
    return _mcp_client

# MCP 클라이언트 종료 함수
async def close_mcp_client():
    """MCP 클라이언트 연결을 안전하게 종료합니다."""
    global _mcp_client
    
    if _mcp_client is not None:
        print("MCP 클라이언트 연결 종료 중...")
        try:
            await _mcp_client.__aexit__(None, None, None)
            print("MCP 클라이언트 연결 종료 완료")
        except Exception as e:
            print(f"MCP 클라이언트 연결 종료 중 오류 발생: {str(e)}")
        finally:
            _mcp_client = None

# MCP 도구 가져오기 함수
async def get_mcp_tools() -> List:
    """MCP 도구를 가져오고 상세 정보를 출력합니다."""
    global _mcp_tools_cache
    
    # 캐시된 도구가 있으면 반환
    if _mcp_tools_cache is not None:
        return _mcp_tools_cache
    
    try:
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
        
        # 캐시에 저장
        _mcp_tools_cache = tools
        return tools
    except Exception as e:
        print(f"도구 가져오기 중 오류 발생: {str(e)}")
        # 오류 발생 시 빈 목록 반환
        return []

# MCP 도구 정보 변환 함수
async def convert_mcp_tools_to_info() -> List[Dict[str, Any]]:
    """MCP 도구를 사용자 친화적인 형식으로 변환합니다."""
    tools = await get_mcp_tools()
    tools_info = []
    
    for tool in tools:
        try:
            tool_info = {
                "name": getattr(tool, "name", "Unknown"),
                "description": getattr(tool, "description", "설명 없음"),
                "parameters": []
            }
            
            # 파라미터 정보 추출
            if hasattr(tool, "args_schema") and tool.args_schema is not None:
                schema_props = getattr(tool.args_schema, "schema", {}).get("properties", {})
                if schema_props:
                    tool_info["parameters"] = list(schema_props.keys())
            
            tools_info.append(tool_info)
        except Exception as e:
            print(f"도구 정보 변환 중 오류: {str(e)}")
    
    return tools_info

# LLM 모델 초기화 함수
async def get_llm():
    """LLM 모델을 초기화하고 반환합니다."""
    global _llm_instance
    
    if _llm_instance is None:
        # 모델 설정 가져오기
        model_name = os.environ.get("VERTEX_MODEL", "gemini-2.0-flash")
        print(f"LLM 모델 초기화: {model_name}")
        
        _llm_instance = ChatVertexAI(
            model=model_name,
            temperature=0.2,
            max_output_tokens=8190
        )
    
    return _llm_instance

# 프롬프트 생성 함수
async def generate_prompt() -> str:
    """사용자 요청에 따른 프롬프트를 생성합니다."""
    # 도구 정보 가져오기 시도
    try:
        # 도구 정보 가져오기 (MCP 서버에서 동적으로)
        tools_info = await convert_mcp_tools_to_info()
        
        # 도구 정보 포맷팅
        tools_text = "\n".join([
            f"{i+1}. {tool['name']}: {tool['description']} (파라미터: {', '.join(tool['parameters']) if tool['parameters'] else '없음'})" 
            for i, tool in enumerate(tools_info)
        ])
        
        if not tools_text:
            tools_text = "현재 사용 가능한 도구가 없습니다. MCP 서버 연결을 확인하세요."
            
    except Exception as e:
        print(f"도구 정보 가져오기 중 오류 발생: {str(e)}")
        tools_text = "도구 정보를 가져오는 중 오류가 발생했습니다. MCP 서버 연결을 확인하세요."
    
    # 프롬프트 템플릿
    prompt_template = """당신은 유능한 스마트홈 비서입니다. 사용자의 요청에 따라 스마트홈 기기를 어떻게 제어할지 계획을 세우고 실행합니다

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
- 사용자에게 최종답변을 줄때에는 행동,행동입력,관찰 등은 주지말고 최종 답변만 전달하세요.
예시:
사용자: "냉장고에 있는 식재료로 요리를 추천해주고 인덕션을 켜줘"
계획:
1. 냉장고에 있는 식재료 목록을 조회합니다. (도구: get_food_items)
2. 식재료를 기반으로 요리를 추천받습니다. (도구: recommend_food 파라미터: [식재료 목록])
3. 추천된 요리의 레시피를 조회합니다. (도구: get_recipe 파라미터: [추천된 요리 이름])
4. 인덕션 상태를 확인합니다. (도구: get_status)
5. 인덕션 전원을 켭니다. (도구: toggle_power)

사용 가능한 도구 목록:
{tools}

"""
    
    # 프롬프트 완성
    prompt = prompt_template.format(tools=tools_text)
    
    return prompt

# 계획 생성 함수
async def generate_agent() -> str:
    """사용자 요청에 대한 계획을 생성합니다."""
    # 프롬프트 생성
    prompt = await generate_prompt()
    
    # LLM 모델 가져오기
    llm = await get_llm()
    tools = await get_mcp_tools()

    _agent_instance = create_react_agent(
            llm, 
            tools, 
            prompt=prompt,
            debug=True  # 디버그 모드 활성화
        )
    
    
    return _agent_instance

# 대화 인터페이스 구현
async def run_conversation_async():
    """대화형 인터페이스 실행 (비동기)"""
    # 에이전트 가져오기
    agent = await generate_agent()
    
    # 대화 이력 초기화
    conversation_history = []
    
    print("스마트홈 AI 비서입니다. 환영합니다. '종료'를 입력하면 대화가 종료됩니다.")
    
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
                print("=" * 50)
                print(last_msg.content)
                print("=" * 50)
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
    agent = await generate_agent()
    
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