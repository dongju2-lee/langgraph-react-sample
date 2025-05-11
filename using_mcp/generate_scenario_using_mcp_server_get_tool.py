#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
DevOps 플래닝 에이전트 (Google Vertex AI 사용)
사용자의 요청을 분석하고 어떤 도구를 어떤 순서로 사용할지 계획을 제시합니다.
Google Vertex AI의 Gemini 모델을 사용합니다.
실제로 도구를 호출하지 않고 계획만 생성합니다.
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

# 환경 변수 로드
load_dotenv()

# 싱글톤 인스턴스
_llm_instance = None
_mcp_client = None
_mcp_tools_cache = None

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
async def generate_prompt(user_request: str) -> str:
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
    prompt_template = """당신은 유능한 데브옵스 엔지니어입니다. 사용자의 요청에 따라 작업을 어떻게 처리할지 계획을 세우는 역할을 합니다.

사용자의 요청을 분석하고, 해당 요청을 처리하기 위해 어떤 도구를 어떤 순서로 사용할지 계획을 제시해주세요.
**실제로 도구를 호출하지 않고, 어떤 도구를 사용할지 설명만 해주세요.**

예시:
사용자: "오더서비스 성능테스트하고 배포해, 그리고 그라파나에서 성능추이좀 알려줘"
계획:
1. k6를 사용하여 오더서비스의 성능 테스트를 실행합니다. (도구: run_k6_performance_test 파라미터: order-service, 50, 30s)
2. 성능 테스트 결과를 확인한 후 ArgoCD를 통해 오더서비스를 배포합니다. (도구: deploy_application 파라미터: order-service)
3. 배포 상태를 확인합니다. (도구: check_deployment_status 파라미터: order-service)
4. Grafana에서 사용 가능한 대시보드 목록을 조회합니다. (도구: search_grafana_dashboards)
5. CPU 사용률 대시보드의 메트릭 정보를 조회하여 성능 추이를 확인합니다. (도구: get_dashboard_metrics 파라미터: cpu-usage-dashboard)

사용 가능한 도구 목록:
{tools}

사용자의 요청을 신중하게 분석하고, 각 작업을 수행하기 위해 필요한 도구와 순서를 명확하게 설명해주세요.
도구 이름과 필요한 파라미터를 정확히 지정해주세요.
한국어로 응답해주세요.
"""
    
    # 프롬프트 완성
    prompt = prompt_template.format(tools=tools_text)
    
    return f"{prompt}\n\n사용자: \"{user_request}\"\n\n대응 계획:"

# 계획 생성 함수
async def generate_plan(user_request: str) -> str:
    """사용자 요청에 대한 계획을 생성합니다."""
    # 프롬프트 생성
    prompt = await generate_prompt(user_request)
    
    # LLM 모델 가져오기
    llm = await get_llm()
    
    # LLM에 요청
    response = llm.invoke(prompt)
    
    return response.content

# 신호 처리기 설정
def setup_signal_handlers():
    """프로그램 종료 시 리소스를 정리하기 위한 신호 처리기를 설정합니다."""
    
    def signal_handler(sig, frame):
        print("\n프로그램 종료 신호를 받았습니다. 리소스를 정리합니다...")
        
        # 클라이언트 연결을 닫기 위한 이벤트 루프 생성
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(close_mcp_client())
        finally:
            loop.close()
            print("리소스 정리 완료. 프로그램을 종료합니다.")
            import sys
            sys.exit(0)
    
    # 종료 신호에 대한 핸들러 등록
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

# 대화형 인터페이스 구현
async def run_planning_conversation():
    """대화형 인터페이스 실행 (비동기)"""
    print("=" * 50)
    print("데브옵스 플래닝 에이전트에 오신 것을 환영합니다.")
    print("사용자의 요청에 따라 어떤 도구를 어떤 순서로 사용할지 계획을 제시합니다.")
    print("'종료'를 입력하면 대화가 종료됩니다.")
    print("=" * 50)
    
    try:
        # MCP 클라이언트 초기화
        await init_mcp_client()
        
        while True:
            # 사용자 입력 받기
            user_input = input("\n사용자: ")
            
            # 종료 조건 확인
            if user_input.lower() in ['종료', 'exit', 'quit']:
                print("대화를 종료합니다. 감사합니다.")
                break
            
            try:
                # 계획 생성
                print("\n계획을 생성 중입니다...")
                plan = await generate_plan(user_input)
                
                # 계획 출력
                print("\n계획:")
                print("-" * 30)
                print(plan)
                print("-" * 30)
                
            except Exception as e:
                print(f"\n오류가 발생했습니다: {str(e)}")
                import traceback
                traceback.print_exc()
    finally:
        # 연결 종료
        await close_mcp_client()

# 예제 쿼리 실행 함수
async def run_example_query(query: str):
    """예제 쿼리를 실행하고 계획을 출력합니다."""
    print(f"\n예제 쿼리: \"{query}\"")
    print("\n계획을 생성 중입니다...")
    
    try:
        # MCP 클라이언트 초기화
        await init_mcp_client()
        
        plan = await generate_plan(query)
        print("\n계획:")
        print("-" * 30)
        print(plan)
        print("-" * 30)
    except Exception as e:
        print(f"\n오류가 발생했습니다: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        # 연결 종료
        await close_mcp_client()

# 메인 비동기 함수
async def main_async():
    """메인 비동기 함수"""
    print("=" * 50)
    print("Google Vertex AI 기반 DevOps 플래닝 에이전트 시작")
    print("=" * 50)
    
    # 신호 처리기 설정
    setup_signal_handlers()
    
    # 모드 선택
    print("\n실행 모드를 선택하세요:")
    print("1: 예제 쿼리 실행")
    print("2: 대화형 인터페이스 실행")
    mode = input("선택 (기본: 2): ").strip() or "2"
    
    try:
        if mode == "1":
            # 예제 쿼리 목록 
            example_queries = [
                "현재 시스템 상태를 확인해줘",
                "오더 서비스를 배포하고 상태를 확인해줘",
                "주문 서비스에 대해 가상 사용자 50명으로 30초 동안 성능 테스트를 실행하고 결과를 분석해줘",
                "GitHub PR 목록을 보여주고 PR #101을 승인해줘",
                "오더서비스 성능테스트하고 배포해, 그리고 그라파나에서 성능추이좀 알려줘"
            ]
            
            print("\n사용 가능한 예제 쿼리:")
            for i, query in enumerate(example_queries, 1):
                print(f"{i}: {query}")
            
            choice = input("실행할 쿼리 번호를 선택하세요 (1-5, 또는 0 입력시 직접 입력): ")
            
            try:
                choice_num = int(choice)
                if 1 <= choice_num <= len(example_queries):
                    await run_example_query(example_queries[choice_num-1])
                elif choice_num == 0:
                    custom_query = input("실행할 쿼리를 입력하세요: ")
                    await run_example_query(custom_query)
                else:
                    print("잘못된 선택입니다.")
            except ValueError:
                print("숫자를 입력해주세요.")
        else:
            # 대화형 인터페이스 실행
            await run_planning_conversation()
    finally:
        # 항상 연결 종료 확인
        await close_mcp_client()

# 컨텍스트 매니저를 사용한 안전한 비동기 작업 실행
@contextlib.asynccontextmanager
async def safe_async_context():
    """안전한 비동기 작업 실행을 위한 컨텍스트 매니저"""
    try:
        yield
    finally:
        await close_mcp_client()

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
    finally:
        # 프로그램이 종료될 때 리소스 정리 (asyncio.run이 종료된 후)
        print("프로그램 종료 시 최종 리소스 정리 중...")
        
        # 비동기 작업이 종료된 이후에는 별도의 정리가 필요 없음
        # (asyncio.run이 내부적으로 loop.close()를 호출함)

if __name__ == "__main__":
    main() 