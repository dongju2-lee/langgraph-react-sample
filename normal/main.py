# 필요한 라이브러리 임포트
import random
import os
import json
import requests
from typing import TypedDict, Annotated, List, Dict, Any, Tuple
from langchain_core.messages import AnyMessage
from langchain_core.tools import Tool
from langchain_google_vertexai import ChatVertexAI
from langgraph.prebuilt import create_react_agent
from langgraph.graph.message import add_messages

# 데브옵스 도구 시뮬레이션 클래스
class DevOpsTools:
    def __init__(self):
        # 시뮬레이션을 위한 데이터 초기화
        self.grafana_dashboards = [
            "cpu-usage-dashboard", 
            "memory-usage-dashboard", 
            "pod-count-dashboard"
        ]
        
        self.grafana_datasources = [
            "prometheus", 
            "loki", 
            "tempo"
        ]
        
        self.argocd_applications = [
            "user-service", 
            "restaurant-service", 
            "order-service"
        ]
        
        self.k6_test_results = {}  # 테스트 번호를 키로 사용해 테스트 결과 저장
        
        self.github_prs = [
            {
                "id": 1,
                "title": "user-service API 엔드포인트 추가",
                "body": "로그인/로그아웃 기능 개선 및 버그 수정",
                "status": "waiting"
            },
            {
                "id": 2,
                "title": "restaurant-service 메뉴 관리 개선",
                "body": "메뉴 추가/수정/삭제 기능 리팩토링",
                "status": "waiting"
            },
            {
                "id": 3,
                "title": "order-service 결제 시스템 연동",
                "body": "신용카드, 페이팔 결제 연동 추가",
                "status": "waiting"
            },
            {
                "id": 4,
                "title": "user-service 회원가입 프로세스 개선",
                "body": "이메일 인증 및 소셜 로그인 기능 추가",
                "status": "waiting"
            }
        ]
    
    def search_grafana_dashboards(self) -> Dict[str, Any]:
        """Grafana 대시보드 목록 검색"""
        return {
            "success": True,
            "dashboards": self.grafana_dashboards
        }
    
    def get_dashboard_metrics(self, dashboard_name: str) -> Dict[str, Any]:
        """특정 Grafana 대시보드의 메트릭 정보 조회"""
        normalized_name = dashboard_name.strip().lower()
        
        if normalized_name not in [d.lower() for d in self.grafana_dashboards]:
            return {"error": f"대시보드 '{dashboard_name}'를 찾을 수 없습니다."}
        
        # 각 대시보드별 랜덤 메트릭 생성
        if "cpu" in normalized_name:
            cpu_usage = random.randint(20, 100)
            return {
                "success": True,
                "dashboard": dashboard_name,
                "metrics": {
                    "cpu_usage": f"{cpu_usage}%",
                    "status": "critical" if cpu_usage > 80 else "normal"
                }
            }
        elif "memory" in normalized_name:
            memory_usage = random.randint(20, 100)
            return {
                "success": True,
                "dashboard": dashboard_name,
                "metrics": {
                    "memory_usage": f"{memory_usage}%",
                    "status": "critical" if memory_usage > 80 else "normal"
                }
            }
        elif "pod" in normalized_name:
            pod_count = random.randint(15, 30)
            return {
                "success": True,
                "dashboard": dashboard_name,
                "metrics": {
                    "pod_count": pod_count,
                    "status": "normal"
                }
            }
        else:
            return {"error": "지원되지 않는 대시보드입니다."}
    
    def get_grafana_datasources(self) -> Dict[str, Any]:
        """Grafana 데이터소스 목록 조회"""
        return {
            "success": True,
            "datasources": self.grafana_datasources
        }
    
    def list_argocd_applications(self) -> Dict[str, Any]:
        """ArgoCD 애플리케이션 목록 조회"""
        return {
            "success": True,
            "applications": self.argocd_applications
        }
    
    def deploy_application(self, app_name: str) -> Dict[str, Any]:
        """ArgoCD 애플리케이션 배포"""
        normalized_name = app_name.strip().lower()
        
        if normalized_name not in [a.lower() for a in self.argocd_applications]:
            return {"error": f"애플리케이션 '{app_name}'을(를) 찾을 수 없습니다."}
        
        # 80% 확률로 배포 성공, 20% 확률로 실패
        if random.random() < 0.8:
            return {
                "success": True,
                "message": f"애플리케이션 '{app_name}'이(가) 성공적으로 배포되었습니다.",
                "deployed_at": "2023-05-15T14:30:45Z",
                "revision": f"main-{random.randint(100000, 999999)}"
            }
        else:
            return {
                "success": False,
                "error": f"애플리케이션 '{app_name}' 배포 중 오류가 발생했습니다.",
                "error_code": f"ERR-{random.randint(1000, 9999)}",
                "suggestion": "로그를 확인하고 다시 시도해보세요."
            }
    
    def run_k6_performance_test(self, service_name: str, virtual_users: int, duration: str) -> Dict[str, Any]:
        """k6 성능 테스트 실행"""
        if not service_name or not virtual_users or not duration:
            return {"error": "서비스 이름, 가상 사용자 수, 테스트 지속 시간이 모두 필요합니다."}
        
        try:
            virtual_users = int(virtual_users)
            if virtual_users <= 0:
                return {"error": "가상 사용자 수는 양수여야 합니다."}
        except ValueError:
            return {"error": f"유효하지 않은 가상 사용자 수: {virtual_users}"}
        
        # 랜덤 테스트 결과 생성
        avg_response_time = random.randint(10, 30)
        max_response_time = random.randint(100, 200)
        test_id = random.randint(1, 2000)
        
        # 테스트 결과 저장
        self.k6_test_results[test_id] = {
            "service": service_name,
            "virtual_users": virtual_users,
            "duration": duration,
            "avg_response_time": avg_response_time,
            "max_response_time": max_response_time,
            "timestamp": "2023-05-15T15:30:45Z"
        }
        
        return {
            "success": True,
            "test_id": test_id,
            "service": service_name,
            "metrics": {
                "virtual_users": virtual_users,
                "duration": duration,
                "avg_response_time": f"{avg_response_time}ms",
                "max_response_time": f"{max_response_time}ms",
                "requests_per_second": random.randint(500, 2000)
            }
        }
    
    def compare_k6_tests(self, test_id1: int, test_id2: int) -> Dict[str, Any]:
        """두 k6 테스트 결과 비교"""
        try:
            test_id1 = int(test_id1)
            test_id2 = int(test_id2)
        except ValueError:
            return {"error": "테스트 ID는 숫자여야 합니다."}
        
        if test_id1 not in self.k6_test_results or test_id2 not in self.k6_test_results:
            return {"error": "하나 이상의 테스트 ID가 존재하지 않습니다."}
        
        # 랜덤 비교 결과 생성
        avg_time_diff = random.randint(1, 30)
        max_time_diff = random.randint(1, 100)
        
        # 무작위로 더 빠른 테스트 선택
        faster_test = test_id1 if random.random() < 0.5 else test_id2
        
        return {
            "success": True,
            "test1": {
                "id": test_id1,
                "service": self.k6_test_results[test_id1]["service"],
                "avg_response_time": f"{self.k6_test_results[test_id1]['avg_response_time']}ms",
                "max_response_time": f"{self.k6_test_results[test_id1]['max_response_time']}ms"
            },
            "test2": {
                "id": test_id2,
                "service": self.k6_test_results[test_id2]["service"],
                "avg_response_time": f"{self.k6_test_results[test_id2]['avg_response_time']}ms",
                "max_response_time": f"{self.k6_test_results[test_id2]['max_response_time']}ms"
            },
            "comparison": {
                "avg_response_time_diff": f"{avg_time_diff}ms",
                "max_response_time_diff": f"{max_time_diff}ms",
                "faster_test": faster_test
            }
        }
    
    def list_github_prs(self) -> Dict[str, Any]:
        """GitHub PR 목록 조회"""
        return {
            "success": True,
            "pull_requests": self.github_prs
        }
    
    def approve_github_pr(self, pr_id: int) -> Dict[str, Any]:
        """GitHub PR 승인"""
        try:
            pr_id = int(pr_id)
        except ValueError:
            return {"error": "PR ID는 숫자여야 합니다."}
        
        for i, pr in enumerate(self.github_prs):
            if pr["id"] == pr_id:
                if pr["status"] == "waiting":
                    self.github_prs[i]["status"] = "approved"
                    return {
                        "success": True,
                        "message": f"PR #{pr_id}가 성공적으로 승인되었습니다.",
                        "pr": self.github_prs[i]
                    }
                else:
                    return {
                        "error": f"PR #{pr_id}는 이미 {pr['status']} 상태입니다."
                    }
        
        return {"error": f"PR #{pr_id}를 찾을 수 없습니다."}

# 도구 인스턴스 생성
devops_tools = DevOpsTools()

# 도구 함수 정의
def search_grafana_dashboards() -> Dict[str, Any]:
    """
    Grafana 대시보드 목록을 검색합니다.
    
    Returns:
        사용 가능한 대시보드 목록을 포함한 딕셔너리
    """
    print("====== [도구 호출] search_grafana_dashboards 도구가 호출되었습니다. ======")
    return devops_tools.search_grafana_dashboards()

def get_dashboard_metrics(dashboard_name: str) -> Dict[str, Any]:
    """
    특정 Grafana 대시보드의 메트릭 정보를 조회합니다.
    
    Args:
        dashboard_name: 조회할 대시보드 이름
        
    Returns:
        대시보드 메트릭 정보를 포함한 딕셔너리
    """
    print(f"====== [도구 호출] get_dashboard_metrics 도구가 호출되었습니다. 대시보드: {dashboard_name} ======")
    return devops_tools.get_dashboard_metrics(dashboard_name)

def get_grafana_datasources() -> Dict[str, Any]:
    """
    Grafana에 연결된 데이터소스 목록을 조회합니다.
    
    Returns:
        데이터소스 목록을 포함한 딕셔너리
    """
    print("====== [도구 호출] get_grafana_datasources 도구가 호출되었습니다. ======")
    return devops_tools.get_grafana_datasources()

def list_argocd_applications() -> Dict[str, Any]:
    """
    ArgoCD 애플리케이션 목록을 조회합니다.
    
    Returns:
        애플리케이션 목록을 포함한 딕셔너리
    """
    print("====== [도구 호출] list_argocd_applications 도구가 호출되었습니다. ======")
    return devops_tools.list_argocd_applications()

def deploy_application(app_name: str) -> Dict[str, Any]:
    """
    ArgoCD를 통해 애플리케이션을 배포합니다.
    
    Args:
        app_name: 배포할 애플리케이션 이름
        
    Returns:
        배포 결과를 포함한 딕셔너리
    """
    print(f"====== [도구 호출] deploy_application 도구가 호출되었습니다. 애플리케이션: {app_name} ======")
    return devops_tools.deploy_application(app_name)

def run_k6_performance_test(service_name: str, virtual_users: int, duration: str) -> Dict[str, Any]:
    """
    k6를 사용하여 성능 테스트를 실행합니다.
    
    Args:
        service_name: 테스트할 서비스 이름
        virtual_users: 가상 사용자 수
        duration: 테스트 지속 시간 (예: "30s", "1m")
        
    Returns:
        테스트 결과를 포함한 딕셔너리
    """
    print(f"====== [도구 호출] run_k6_performance_test 도구가 호출되었습니다. 서비스: {service_name}, 사용자: {virtual_users}, 시간: {duration} ======")
    return devops_tools.run_k6_performance_test(service_name, virtual_users, duration)

def compare_k6_tests(test_id1: int, test_id2: int) -> Dict[str, Any]:
    """
    두 k6 테스트 결과를 비교합니다.
    
    Args:
        test_id1: 첫 번째 테스트 ID
        test_id2: 두 번째 테스트 ID
        
    Returns:
        테스트 비교 결과를 포함한 딕셔너리
    """
    print(f"====== [도구 호출] compare_k6_tests 도구가 호출되었습니다. 테스트 ID: {test_id1}, {test_id2} ======")
    return devops_tools.compare_k6_tests(test_id1, test_id2)

def list_github_prs() -> Dict[str, Any]:
    """
    GitHub 풀 리퀘스트 목록을 조회합니다.
    
    Returns:
        PR 목록을 포함한 딕셔너리
    """
    print("====== [도구 호출] list_github_prs 도구가 호출되었습니다. ======")
    return devops_tools.list_github_prs()

def approve_github_pr(pr_id: int) -> Dict[str, Any]:
    """
    GitHub 풀 리퀘스트를 승인합니다.
    
    Args:
        pr_id: 승인할 PR ID
        
    Returns:
        승인 결과를 포함한 딕셔너리
    """
    print(f"====== [도구 호출] approve_github_pr 도구가 호출되었습니다. PR ID: {pr_id} ======")
    return devops_tools.approve_github_pr(pr_id)

# LangChain Tool 객체로 변환
search_grafana_dashboards_tool = Tool.from_function(
    func=search_grafana_dashboards,
    name="search_grafana_dashboards",
    description="Grafana 대시보드 목록을 검색합니다. 사용 가능한 대시보드 이름 목록을 반환합니다."
)

get_dashboard_metrics_tool = Tool.from_function(
    func=get_dashboard_metrics,
    name="get_dashboard_metrics",
    description="Grafana 대시보드의 메트릭 정보를 조회합니다. 대시보드 이름을 입력하면 CPU 사용률, 메모리 사용률, Pod 개수 등의 메트릭을 반환합니다."
)

get_grafana_datasources_tool = Tool.from_function(
    func=get_grafana_datasources,
    name="get_grafana_datasources",
    description="Grafana에 연결된 데이터소스 목록을 조회합니다. 프로메테우스, 로키, 템포 등의 데이터소스 정보를 반환합니다."
)

list_argocd_applications_tool = Tool.from_function(
    func=list_argocd_applications,
    name="list_argocd_applications",
    description="ArgoCD에 등록된 애플리케이션 목록을 조회합니다. 유저 서비스, 레스토랑 서비스, 오더 서비스 등의 등록된 애플리케이션을 반환합니다."
)

deploy_application_tool = Tool.from_function(
    func=deploy_application,
    name="deploy_application",
    description="ArgoCD를 통해 애플리케이션을 배포합니다. 애플리케이션 이름을 입력하면 해당 애플리케이션을 배포하고 결과를 반환합니다."
)

run_k6_performance_test_tool = Tool.from_function(
    func=run_k6_performance_test,
    name="run_k6_performance_test",
    description="k6를 사용하여 성능 테스트를 실행합니다. 서비스 이름, 가상 사용자 수, 테스트 지속 시간을 입력하면 테스트 결과와 테스트 ID를 반환합니다."
)

compare_k6_tests_tool = Tool.from_function(
    func=compare_k6_tests,
    name="compare_k6_tests",
    description="두 k6 테스트 결과를 비교합니다. 두 테스트 ID를 입력하면 응답 시간 차이와 더 빠른 테스트를 반환합니다."
)

list_github_prs_tool = Tool.from_function(
    func=list_github_prs,
    name="list_github_prs",
    description="GitHub 풀 리퀘스트 목록을 조회합니다. 현재 오픈된 PR 목록과 상태를 반환합니다."
)

approve_github_pr_tool = Tool.from_function(
    func=approve_github_pr,
    name="approve_github_pr",
    description="GitHub 풀 리퀘스트를 승인합니다. PR ID를 입력하면 해당 PR을 승인하고 결과를 반환합니다."
)

# 도구 목록 정의
tools = [
    search_grafana_dashboards_tool,
    get_dashboard_metrics_tool,
    get_grafana_datasources_tool,
    list_argocd_applications_tool,
    deploy_application_tool,
    run_k6_performance_test_tool,
    compare_k6_tests_tool,
    list_github_prs_tool,
    approve_github_pr_tool
]

# Google Vertex AI Gemini 2.0 Flash 모델 초기화
# 주의: 실제 사용 시에는 Google Cloud 인증 설정 필요
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "path/to/your/service-account-key.json"
model = ChatVertexAI(
    model_name="gemini-2.0-flash",
    # project="your-project-id",  # 실제 프로젝트 ID 입력 필요
    temperature=0
)

# ReAct 에이전트 프롬프트
prompt = """당신은 유능한 데브옵스 엔지니어입니다. 사용자의 요청에 따라 시스템 모니터링, 배포 관리, 성능 테스트, 코드 리뷰를 수행합니다.
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

모니터링:
- 여러 Grafana 대시보드를 통해 시스템 상태를 모니터링합니다.
- CPU 사용률, 메모리 사용률, Pod 개수 등의 메트릭을 확인할 수 있습니다.
- 프로메테우스, 로키, 템포 등의 데이터소스를 사용하여 정보를 수집합니다.

애플리케이션 배포:
- ArgoCD를 통해 애플리케이션을 배포합니다.
- 유저 서비스, 레스토랑 서비스, 오더 서비스 등의 애플리케이션이 있습니다.
- 배포는 80% 확률로 성공하고, 20% 확률로 실패할 수 있습니다.

성능 테스트:
- k6를 사용하여 서비스의 성능을 테스트합니다.
- 서비스 이름, 가상 사용자 수, 테스트 지속 시간을 지정하여 테스트를 실행합니다.
- 평균 응답 시간, 최고 응답 시간 등의 메트릭을 확인할 수 있습니다.
- 서로 다른 테스트 결과를 비교하여 성능 향상을 확인할 수 있습니다.

코드 리뷰:
- GitHub 풀 리퀘스트(PR)를 통해 코드 변경사항을 검토합니다.
- PR 목록을 확인하고, 필요한 경우 승인할 수 있습니다.
- PR은 기본적으로 대기 상태에서 시작하여 승인 상태로 변경할 수 있습니다.

사용 가능한 도구:
1. search_grafana_dashboards: Grafana 대시보드 목록을 검색합니다.
2. get_dashboard_metrics: 특정 Grafana 대시보드의 메트릭 정보를 조회합니다.
3. get_grafana_datasources: Grafana에 연결된 데이터소스 목록을 조회합니다.
4. list_argocd_applications: ArgoCD 애플리케이션 목록을 조회합니다.
5. deploy_application: ArgoCD를 통해 애플리케이션을 배포합니다.
6. run_k6_performance_test: k6를 사용하여 성능 테스트를 실행합니다.
7. compare_k6_tests: 두 k6 테스트 결과를 비교합니다.
8. list_github_prs: GitHub 풀 리퀘스트 목록을 조회합니다.
9. approve_github_pr: GitHub 풀 리퀘스트를 승인합니다.
"""

# LangGraph ReAct 에이전트 생성
graph = create_react_agent(
    model,
    tools=tools,
    prompt=prompt,
    debug=True  # 디버그 모드 활성화 (실행 과정 확인)
)

# 간단한 대화 인터페이스 구현
def run_conversation():
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
        conversation_history.append({"role": "user", "content": user_input})
        
        # 에이전트에 입력 전달
        inputs = {"messages": conversation_history}
        
        try:
            # 에이전트 응답 얻기 (스트리밍 모드)
            print("\n엔지니어: ", end="")
            
            # 마지막 응답 저장용
            final_response = None
            
            for chunk in graph.stream(inputs, stream_mode="values"):
                if "messages" in chunk and chunk["messages"]:
                    # 마지막 메시지 가져오기
                    last_msg = chunk["messages"][-1]
                    if hasattr(last_msg, "content") and last_msg.content:
                        print(last_msg.content, end="")
                        final_response = chunk
            
            print()  # 줄바꿈
            
            # 응답을 대화 이력에 추가
            if final_response:
                conversation_history = final_response["messages"]
            
        except Exception as e:
            print(f"\n오류가 발생했습니다: {str(e)}")

# 메인 함수
def main():
    print("=== 데브옵스 엔지니어 에이전트 시작 ===")
    
    # 예제 실행
    example_query = "현재 시스템 상태를 확인해줘"
    print(f"\n예제 쿼리: {example_query}")
    
    # 입력 메시지 구성
    inputs = {"messages": [{"role": "user", "content": example_query}]}
    
    # 에이전트 실행
    print("\n에이전트 응답:")
    for chunk in graph.stream(inputs, stream_mode="values"):
        if "messages" in chunk and chunk["messages"]:
            last_msg = chunk["messages"][-1]
            if isinstance(last_msg, str):
                print(last_msg, end="")
            else:
                # role 또는 type 속성 가져오기
                role = getattr(last_msg, "role", None) or getattr(last_msg, "type", None)
                if role != "human":  # human 메시지는 사용자 메시지라 출력 안 함
                    print(last_msg.content, end="")

    
    # 대화형 인터페이스 실행
    print("\n\n=== 대화형 인터페이스 시작 ===")
    run_conversation()

if __name__ == "__main__":
    main()
