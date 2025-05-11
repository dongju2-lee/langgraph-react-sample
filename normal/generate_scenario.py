# 필요한 라이브러리 임포트
import random
import os
import json
from typing import List, Dict, Any, Tuple

from langchain_google_vertexai import ChatVertexAI

# 시나리오 생성 클래스
class ScenarioGenerator:
    def __init__(self):
        # 사용 가능한 도구 목록
        self.available_tools = [
            {
                "name": "search_grafana_dashboards",
                "description": "Grafana 대시보드 목록을 검색합니다.",
                "parameters": []
            },
            {
                "name": "get_dashboard_metrics",
                "description": "특정 Grafana 대시보드의 메트릭 정보를 조회합니다.",
                "parameters": ["대시보드 이름"]
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
                "parameters": ["애플리케이션 이름"]
            },
            {
                "name": "run_k6_performance_test",
                "description": "k6를 사용하여 성능 테스트를 실행합니다.",
                "parameters": ["서비스 이름", "가상 사용자 수", "테스트 지속 시간"]
            },
            {
                "name": "compare_k6_tests",
                "description": "두 k6 테스트 결과를 비교합니다.",
                "parameters": ["테스트 ID 1", "테스트 ID 2"]
            },
            {
                "name": "list_github_prs",
                "description": "GitHub 풀 리퀘스트 목록을 조회합니다.",
                "parameters": []
            },
            {
                "name": "approve_github_pr",
                "description": "GitHub 풀 리퀘스트를 승인합니다.",
                "parameters": ["PR ID"]
            }
        ]
        
        # 가용 리소스 정보
        self.resources = {
            "grafana_dashboards": ["cpu-usage-dashboard", "memory-usage-dashboard", "pod-count-dashboard"],
            "grafana_datasources": ["prometheus", "loki", "tempo"],
            "argocd_applications": ["user-service", "restaurant-service", "order-service"],
            "github_prs": [
                {"id": 1, "title": "user-service API 엔드포인트 추가"},
                {"id": 2, "title": "restaurant-service 메뉴 관리 개선"},
                {"id": 3, "title": "order-service 결제 시스템 연동"},
                {"id": 4, "title": "user-service 회원가입 프로세스 개선"}
            ]
        }
    
    def get_tool_info(self, tool_name: str) -> Dict[str, Any]:
        """도구 이름으로 도구 정보 조회"""
        for tool in self.available_tools:
            if tool["name"] == tool_name:
                return tool
        return None
    
    def format_tool_usage(self, tool_name: str, parameters: List[str] = None) -> str:
        """도구 사용 방법 포맷팅"""
        tool_info = self.get_tool_info(tool_name)
        if not tool_info:
            return f"알 수 없는 도구: {tool_name}"
        
        if not parameters:
            parameters = []
        
        formatted_params = ""
        if parameters:
            formatted_params = f" 파라미터: {', '.join(parameters)}"
        
        return f"• {tool_info['description']} (도구: {tool_name}{formatted_params})"

# Google Vertex AI Gemini 모델 초기화
model = ChatVertexAI(
    model_name="gemini-2.0-flash",
    # project="your-project-id",  # 실제 프로젝트 ID 입력 필요
    temperature=0.2
)

# 시나리오 생성기 초기화
scenario_generator = ScenarioGenerator()

# 프롬프트 템플릿
prompt_template = """당신은 유능한 데브옵스 엔지니어입니다. 사용자의 요청에 따라 작업을 어떻게 처리할지 계획을 세우는 역할을 합니다.

사용자의 요청을 분석하고, 해당 요청을 처리하기 위해 어떤 도구를 어떤 순서로 사용할지 계획을 제시해주세요.
**실제로 도구를 호출하지 않고, 어떤 도구를 사용할지 설명만 해주세요.**

예시:
사용자: "오더서비스 성능테스트하고 배포해, 그리고 그라파나에서 성능추이좀 알려줘"
계획:
1. k6를 사용하여 오더서비스의 성능 테스트를 실행합니다. (도구: run_k6_performance_test 파라미터: order-service, 50, 30s)
2. 성능 테스트 결과를 확인한 후 ArgoCD를 통해 오더서비스를 배포합니다. (도구: deploy_application 파라미터: order-service)
3. Grafana에서 사용 가능한 대시보드 목록을 조회합니다. (도구: search_grafana_dashboards)
4. CPU 사용률 대시보드의 메트릭 정보를 조회하여 성능 추이를 확인합니다. (도구: get_dashboard_metrics 파라미터: cpu-usage-dashboard)

사용 가능한 도구 목록:
{tools}

사용 가능한 리소스:
- Grafana 대시보드: {grafana_dashboards}
- Grafana 데이터소스: {grafana_datasources}
- ArgoCD 애플리케이션: {argocd_applications}
- GitHub 풀 리퀘스트: {github_prs}

사용자의 요청을 신중하게 분석하고, 각 작업을 수행하기 위해 필요한 도구와 순서를 명확하게 설명해주세요.
도구 이름과 필요한 파라미터를 정확히 지정해주세요.
"""

# 프롬프트 생성 함수
def generate_prompt(user_request: str) -> str:
    """사용자 요청에 따른 프롬프트 생성"""
    tools_text = "\n".join([f"{i+1}. {tool['name']}: {tool['description']} (파라미터: {', '.join(tool['parameters']) if tool['parameters'] else '없음'})" 
                          for i, tool in enumerate(scenario_generator.available_tools)])
    
    grafana_dashboards = ", ".join(scenario_generator.resources["grafana_dashboards"])
    grafana_datasources = ", ".join(scenario_generator.resources["grafana_datasources"])
    argocd_applications = ", ".join(scenario_generator.resources["argocd_applications"])
    github_prs = ", ".join([f"#{pr['id']} ({pr['title']})" for pr in scenario_generator.resources["github_prs"]])
    
    prompt = prompt_template.format(
        tools=tools_text,
        grafana_dashboards=grafana_dashboards,
        grafana_datasources=grafana_datasources,
        argocd_applications=argocd_applications,
        github_prs=github_prs
    )
    
    return f"{prompt}\n\n사용자: \"{user_request}\"\n\n대응 계획:"

# 시나리오 생성 함수
def generate_scenario(user_request: str) -> str:
    """사용자 요청에 대한 시나리오 생성"""
    prompt = generate_prompt(user_request)
    
    # AI 모델에 요청
    response = model.invoke(prompt)
    
    return response.content

# 대화형 인터페이스
def run_scenario_conversation():
    print("=== 데브옵스 시나리오 생성기 ===")
    print("사용자의 요청에 따라 어떤 도구를 어떤 순서로 사용할지 계획을 제시합니다.")
    print("'종료'를 입력하면 대화가 종료됩니다.")
    
    while True:
        user_input = input("\n사용자: ")
        
        if user_input.lower() in ['종료', 'exit', 'quit']:
            print("대화를 종료합니다. 감사합니다.")
            break
        
        try:
            scenario = generate_scenario(user_input)
            print(f"\n시나리오 계획:\n{scenario}")
        except Exception as e:
            print(f"\n오류가 발생했습니다: {str(e)}")

# 예제 실행
def run_example():
    example_query = "오더서비스 성능테스트하고 배포해, 그리고 그라파나에서 성능추이좀 알려줘"
    print(f"\n예제 쿼리: \"{example_query}\"")
    
    try:
        scenario = generate_scenario(example_query)
        print(f"\n시나리오 계획:\n{scenario}")
    except Exception as e:
        print(f"\n오류가 발생했습니다: {str(e)}")

# 메인 함수
def main():
    # 예제 실행
    run_example()
    
    print("\n\n=== 대화형 인터페이스 시작 ===")
    # 대화형 인터페이스 실행
    run_scenario_conversation()

if __name__ == "__main__":
    main() 