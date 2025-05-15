import asyncio
from workflow.plan_execute_graph import get_workflow
from langchain_core.messages import HumanMessage

async def main():
    workflow = get_workflow()
    print("스마트홈 쿠킹 에이전트에 오신 것을 환영합니다!")
    state = None
    while True:
        if state is None:
            user_input = input("👤 사용자: ")
            if user_input.strip().lower() in ["exit", "quit"]:
                break
            state = {
                "input": user_input,
                "messages": [HumanMessage(content=user_input)]
            }
        result = await workflow.ainvoke(state)
        for step, msg in result.get("past_steps", []):
            print(f"📝 {step}\n🤖 {msg}")
        if result.get("response"):
            print("✅", result["response"])
            state = None  # 플로우 종료 후 초기화
        else:
            # 사용자 입력 대기 (예: 대체재, 진행 여부 등)
            user_input = input("👤 사용자(추가 답변): ")
            state["messages"].append(HumanMessage(content=user_input))

if __name__ == "__main__":
    asyncio.run(main())
