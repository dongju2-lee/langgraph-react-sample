#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
DevOps 플래닝 에이전트 (Google Vertex AI 사용)
사용자의 요청을 분석하고 어떤 도구를 어떤 순서로 사용할지 계획을 제시합니다.
Google Vertex AI의 Gemini 모델을 사용합니다.
실제로 도구를 호출하지 않고 계획만 생성합니다.
"""

import os
import asyncio
from typing import Dict, List, Any

from langchain_google_vertexai import ChatVertexAI
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
DevOps 플래닝 에이전트 (Google Vertex AI 사용)
사용자의 요청을 분석하고 어떤 도구를 어떤 순서로 사용할지 계획을 제시합니다.
Google Vertex AI의 Gemini 모델을 사용합니다.
실제로 도구를 호출하지 않고 계획만 생성합니다.
"""

import os
import asyncio
from typing import Dict, List, Any

from langchain_google_vertexai import ChatVertexAI
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 싱글톤 인스턴스
_llm_instance = None

# 가용 리소스 정보
RESOURCES = {
    "grafana_dashboards": ["cpu-usage-dashboard", "memory-usage-dashboard", "pod-count-dashboard"],
    "grafana_datasources": ["prometheus", "loki", "tempo"],
    "argocd_applications": ["user-service", "restaurant-service", "order-service", "payment-service", "delivery-service", "notification-service"],
    "github_prs": [
        {"id": 101, "title": "사용자 인증 기능 개선"},
        {"id": 102, "title": "주문 서비스 성능 최적화"},
        {"id": 103, "title": "레스토랑 검색 API 추가"}
    ]
}

# 기본 도구 정보
def get_tools_info() -> List[Dict[str, Any]]:
    """도구 정보를 반환합니다."""
    return [
        {
            "name": "search_grafana_dashboards",
            "description": "Grafana 대시보드 목록을 검색합니다.",
            "parameters": []
        },
        {
            "name": "get_dashboard_metrics",
            "description": "특정 Grafana 대시보드의 메트릭 정보를 조회합니다.",
            "parameters": ["dashboard_name"]
        },
        {
            "name": "get_grafana_datasources",
            "description": "Grafana에 연결된 데이터소스 목록을 조회합니다.",
            "parameters": []
        },
        {
            "name": "list_argocd_applications",
            "description": "ArgoCD 애플리케이션 목록을 조회합니다.",
            "parameters": []
        },
        {
            "name": "deploy_application",
            "description": "ArgoCD를 통해 애플리케이션을 배포합니다.",
            "parameters": ["app_name"]
        },
        {
            "name": "check_deployment_status",
            "description": "배포 중인 애플리케이션의 현재 상태를 확인합니다.",
            "parameters": ["app_name"]
        },
        {
            "name": "run_k6_performance_test",
            "description": "k6를 사용하여 성능 테스트를 실행합니다.",
            "parameters": ["service_name", "virtual_users", "duration"]
        },
        {
            "name": "compare_k6_tests",
            "description": "두 k6 테스트 결과를 비교합니다.",
            "parameters": ["test_id1", "test_id2"]
        },
        {
            "name": "list_github_prs",
            "description": "GitHub 풀 리퀘스트 목록을 조회합니다.",
            "parameters": []
        },
        {
            "name": "approve_github_pr",
            "description": "GitHub 풀 리퀘스트를 승인합니다.",
            "parameters": ["pr_id"]
        }
    ]

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
    # 도구 정보 사용
    tools_info = get_tools_info()
    
    # 도구 정보 포맷팅
    tools_text = "\n".join([
        f"{i+1}. {tool['name']}: {tool['description']} (파라미터: {', '.join(tool['parameters']) if tool['parameters'] else '없음'})" 
        for i, tool in enumerate(tools_info)
    ])
    
    # 리소스 정보 포맷팅
    grafana_dashboards = ", ".join(RESOURCES["grafana_dashboards"])
    grafana_datasources = ", ".join(RESOURCES["grafana_datasources"])
    argocd_applications = ", ".join(RESOURCES["argocd_applications"])
    github_prs = ", ".join([f"#{pr['id']} ({pr['title']})" for pr in RESOURCES["github_prs"]])
    
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

사용 가능한 리소스:
- Grafana 대시보드: {grafana_dashboards}
- Grafana 데이터소스: {grafana_datasources}
- ArgoCD 애플리케이션: {argocd_applications}
- GitHub 풀 리퀘스트: {github_prs}

사용자의 요청을 신중하게 분석하고, 각 작업을 수행하기 위해 필요한 도구와 순서를 명확하게 설명해주세요.
도구 이름과 필요한 파라미터를 정확히 지정해주세요.
한국어로 응답해주세요.
"""
    
    # 프롬프트 완성
    prompt = prompt_template.format(
        tools=tools_text,
        grafana_dashboards=grafana_dashboards,
        grafana_datasources=grafana_datasources,
        argocd_applications=argocd_applications,
        github_prs=github_prs
    )
    
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

# 대화형 인터페이스 구현
async def run_planning_conversation():
    """대화형 인터페이스 실행 (비동기)"""
    print("=" * 50)
    print("데브옵스 플래닝 에이전트에 오신 것을 환영합니다.")
    print("사용자의 요청에 따라 어떤 도구를 어떤 순서로 사용할지 계획을 제시합니다.")
    print("'종료'를 입력하면 대화가 종료됩니다.")
    print("=" * 50)
    
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

# 예제 쿼리 실행 함수
async def run_example_query(query: str):
    """예제 쿼리를 실행하고 계획을 출력합니다."""
    print(f"\n예제 쿼리: \"{query}\"")
    print("\n계획을 생성 중입니다...")
    
    try:
        plan = await generate_plan(query)
        print("\n계획:")
        print("-" * 30)
        print(plan)
        print("-" * 30)
    except Exception as e:
        print(f"\n오류가 발생했습니다: {str(e)}")
        import traceback
        traceback.print_exc()

# 메인 비동기 함수
async def main_async():
    """메인 비동기 함수"""
    print("=" * 50)
    print("Google Vertex AI 기반 DevOps 플래닝 에이전트 시작")
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
            "주문 서비스에 대해 가상 사용자 50명으로 30초 동안 성능 테스트를 실행하고 결과를 분석해줘",
            "GitHub PR 목록을 보여주고 첫 번째 PR을 승인해줘",
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

# 싱글톤 인스턴스
_llm_instance = None

# 가용 리소스 정보
RESOURCES = {
    "grafana_dashboards": ["cpu-usage-dashboard", "memory-usage-dashboard", "pod-count-dashboard"],
    "grafana_datasources": ["prometheus", "loki", "tempo"],
    "argocd_applications": ["user-service", "restaurant-service", "order-service", "payment-service", "delivery-service", "notification-service"],
    "github_prs": [
        {"id": 101, "title": "사용자 인증 기능 개선"},
        {"id": 102, "title": "주문 서비스 성능 최적화"},
        {"id": 103, "title": "레스토랑 검색 API 추가"}
    ]
}

# 기본 도구 정보
def get_tools_info() -> List[Dict[str, Any]]:
    """도구 정보를 반환합니다."""
    return [
        {
            "name": "search_grafana_dashboards",
            "description": "Grafana 대시보드 목록을 검색합니다.",
            "parameters": []
        },
        {
            "name": "get_dashboard_metrics",
            "description": "특정 Grafana 대시보드의 메트릭 정보를 조회합니다.",
            "parameters": ["dashboard_name"]
        },
        {
            "name": "get_grafana_datasources",
            "description": "Grafana에 연결된 데이터소스 목록을 조회합니다.",
            "parameters": []
        },
        {
            "name": "list_argocd_applications",
            "description": "ArgoCD 애플리케이션 목록을 조회합니다.",
            "parameters": []
        },
        {
            "name": "deploy_application",
            "description": "ArgoCD를 통해 애플리케이션을 배포합니다.",
            "parameters": ["app_name"]
        },
        {
            "name": "check_deployment_status",
            "description": "배포 중인 애플리케이션의 현재 상태를 확인합니다.",
            "parameters": ["app_name"]
        },
        {
            "name": "run_k6_performance_test",
            "description": "k6를 사용하여 성능 테스트를 실행합니다.",
            "parameters": ["service_name", "virtual_users", "duration"]
        },
        {
            "name": "compare_k6_tests",
            "description": "두 k6 테스트 결과를 비교합니다.",
            "parameters": ["test_id1", "test_id2"]
        },
        {
            "name": "list_github_prs",
            "description": "GitHub 풀 리퀘스트 목록을 조회합니다.",
            "parameters": []
        },
        {
            "name": "approve_github_pr",
            "description": "GitHub 풀 리퀘스트를 승인합니다.",
            "parameters": ["pr_id"]
        }
    ]

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
    # 도구 정보 사용
    tools_info = get_tools_info()
    
    # 도구 정보 포맷팅
    tools_text = "\n".join([
        f"{i+1}. {tool['name']}: {tool['description']} (파라미터: {', '.join(tool['parameters']) if tool['parameters'] else '없음'})" 
        for i, tool in enumerate(tools_info)
    ])
    
    # 리소스 정보 포맷팅
    grafana_dashboards = ", ".join(RESOURCES["grafana_dashboards"])
    grafana_datasources = ", ".join(RESOURCES["grafana_datasources"])
    argocd_applications = ", ".join(RESOURCES["argocd_applications"])
    github_prs = ", ".join([f"#{pr['id']} ({pr['title']})" for pr in RESOURCES["github_prs"]])
    
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

사용 가능한 리소스:
- Grafana 대시보드: {grafana_dashboards}
- Grafana 데이터소스: {grafana_datasources}
- ArgoCD 애플리케이션: {argocd_applications}
- GitHub 풀 리퀘스트: {github_prs}

사용자의 요청을 신중하게 분석하고, 각 작업을 수행하기 위해 필요한 도구와 순서를 명확하게 설명해주세요.
도구 이름과 필요한 파라미터를 정확히 지정해주세요.
한국어로 응답해주세요.
"""
    
    # 프롬프트 완성
    prompt = prompt_template.format(
        tools=tools_text,
        grafana_dashboards=grafana_dashboards,
        grafana_datasources=grafana_datasources,
        argocd_applications=argocd_applications,
        github_prs=github_prs
    )
    
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

# 대화형 인터페이스 구현
async def run_planning_conversation():
    """대화형 인터페이스 실행 (비동기)"""
    print("=" * 50)
    print("데브옵스 플래닝 에이전트에 오신 것을 환영합니다.")
    print("사용자의 요청에 따라 어떤 도구를 어떤 순서로 사용할지 계획을 제시합니다.")
    print("'종료'를 입력하면 대화가 종료됩니다.")
    print("=" * 50)
    
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

# 예제 쿼리 실행 함수
async def run_example_query(query: str):
    """예제 쿼리를 실행하고 계획을 출력합니다."""
    print(f"\n예제 쿼리: \"{query}\"")
    print("\n계획을 생성 중입니다...")
    
    try:
        plan = await generate_plan(query)
        print("\n계획:")
        print("-" * 30)
        print(plan)
        print("-" * 30)
    except Exception as e:
        print(f"\n오류가 발생했습니다: {str(e)}")
        import traceback
        traceback.print_exc()

# 메인 비동기 함수
async def main_async():
    """메인 비동기 함수"""
    print("=" * 50)
    print("Google Vertex AI 기반 DevOps 플래닝 에이전트 시작")
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
            "주문 서비스에 대해 가상 사용자 50명으로 30초 동안 성능 테스트를 실행하고 결과를 분석해줘",
            "GitHub PR 목록을 보여주고 첫 번째 PR을 승인해줘",
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