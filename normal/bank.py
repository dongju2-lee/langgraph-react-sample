# 필요한 라이브러리 임포트
import random
import os
from typing import TypedDict, Annotated, List, Dict, Any
from langchain_core.messages import AnyMessage
from langchain_core.tools import Tool
from langchain_google_vertexai import ChatVertexAI
from langgraph.prebuilt import create_react_agent
from langgraph.graph.message import add_messages

# 간단한 데이터베이스 시뮬레이션
class SimpleDB:
    def __init__(self):
        # 고객 정보 초기화
        self.customers = {
            "1": {"customer_id": "1", "name": "동주", "status": "active"},
            "2": {"customer_id": "2", "name": "창희", "status": "active"},
            "3": {"customer_id": "3", "name": "지영", "status": "active"},
        }
        
        # 계좌 정보 초기화 (고객 ID를 키로 사용)
        self.accounts = {
            "1": {"balance": random.randint(1, 500000), "currency": "KRW"},
            "2": {"balance": random.randint(1, 500000), "currency": "KRW"},
            "3": {"balance": random.randint(1, 500000), "currency": "KRW"},
        }
    
    def get_customer_by_name(self, name: str) -> Dict[str, Any]:
        """이름으로 고객 조회"""
        normalized_name = name.strip()
        for customer_id, data in self.customers.items():
            if normalized_name in data["name"]:
                return data
        return {"error": f"고객 '{name}'을(를) 찾을 수 없습니다."}
    
    def get_balance(self, customer_id: str) -> Dict[str, Any]:
        """고객 ID로 계좌 잔액 조회"""
        if customer_id in self.accounts:
            result = self.accounts[customer_id].copy()
            result["customer_id"] = customer_id
            result["customer_name"] = self.customers[customer_id]["name"]
            return result
        return {"error": f"유효하지 않은 고객 번호: {customer_id}"}
    
    def deposit(self, customer_id: str, amount: int) -> Dict[str, Any]:
        """고객 계좌에 입금"""
        try:
            amount = int(amount)
            if amount <= 0:
                return {"error": "입금액은 양수여야 합니다."}
        except:
            return {"error": f"유효하지 않은 입금액: {amount}"}
        
        if customer_id in self.accounts:
            self.accounts[customer_id]["balance"] += amount
            return {
                "success": True,
                "message": f"고객 {self.customers[customer_id]['name']}({customer_id})의 계좌에 {amount}원이 성공적으로 입금되었습니다.",
                "customer_id": customer_id,
                "customer_name": self.customers[customer_id]["name"],
                "new_balance": self.accounts[customer_id]["balance"],
                "amount": amount
            }
        return {"error": f"유효하지 않은 고객 번호: {customer_id}"}

# 데이터베이스 인스턴스 생성
db = SimpleDB()

# 도구 함수 정의
def search_customer(name: str) -> Dict[str, Any]:
    """
    고객 이름으로 고객 번호를 조회합니다.
    
    Args:
        name: 조회할 고객의 이름
        
    Returns:
        고객 정보를 포함한 딕셔너리
    """
    return db.get_customer_by_name(name)

def check_balance(customer_id: str) -> Dict[str, Any]:
    """
    고객 번호로 계좌 잔액을 조회합니다.
    
    Args:
        customer_id: 잔액을 조회할 고객 번호
        
    Returns:
        잔액 정보를 포함한 딕셔너리
    """
    return db.get_balance(customer_id)

def deposit_money(customer_id: str, amount: int) -> Dict[str, Any]:
    """
    고객 계좌에 돈을 입금합니다.
    
    Args:
        customer_id: 입금할 고객 번호
        amount: 입금할 금액
        
    Returns:
        입금 결과를 포함한 딕셔너리
    """
    return db.deposit(customer_id, amount)

# LangChain Tool 객체로 변환
search_customer_tool = Tool.from_function(
    func=search_customer,
    name="search_customer",
    description="고객 이름으로 고객 번호를 조회합니다. 이름을 입력하면 고객 번호와 정보를 반환합니다."
)

check_balance_tool = Tool.from_function(
    func=check_balance,
    name="check_balance",
    description="고객 번호로 계좌 잔액을 조회합니다. 고객 번호를 입력하면 잔액 정보를 반환합니다."
)

deposit_money_tool = Tool.from_function(
    func=deposit_money,
    name="deposit_money",
    description="고객 계좌에 돈을 입금합니다. 고객 번호와 입금액을 입력하면 입금 결과를 반환합니다."
)

# 도구 목록 정의
tools = [search_customer_tool, check_balance_tool, deposit_money_tool]

# Google Vertex AI Gemini 2.0 Flash 모델 초기화
# 주의: 실제 사용 시에는 Google Cloud 인증 설정 필요
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "path/to/your/service-account-key.json"
model = ChatVertexAI(
    model_name="gemini-2.0-flash",
    # project="your-project-id",  # 실제 프로젝트 ID 입력 필요
    temperature=0
)

# ReAct 에이전트 프롬프트
prompt = """당신은 유능한 금융 비서입니다. 사용자의 요청에 따라 고객 정보와 계좌 정보를 조회하고 관리합니다.
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

고객 정보:
- 동주: 고객 번호 1
- 창희: 고객 번호 2
- 지영: 고객 번호 3

사용 가능한 도구:
1. search_customer: 고객 이름으로 고객 정보를 조회합니다.
2. check_balance: 고객 번호로 계좌 잔액을 조회합니다.
3. deposit_money: 고객 계좌에 돈을 입금합니다.
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
    
    print("금융 비서 에이전트에 오신 것을 환영합니다. '종료'를 입력하면 대화가 종료됩니다.")
    
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
            print("\n비서: ", end="")
            
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
    print("=== 금융 비서 에이전트 시작 ===")
    
    # # 예제 실행
    example_query = "동주라는 사용자 지금 계좌에 얼마있지?"
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
