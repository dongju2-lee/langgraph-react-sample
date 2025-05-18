from graph.main_graph import build_main_graph
from utils.session import create_session
from utils.logging import get_logger
import asyncio
from langchain_core.messages import HumanMessage
from langfuse.callback import CallbackHandler

langfuse_handler = CallbackHandler(
    public_key="",
    secret_key="s",
    host=""
)

async def main():
    session_id = create_session()
    logger = get_logger(session_id)

    # 그래프 빌드 및 컴파일
    graph = build_main_graph()
    graph = graph.compile()

    # 상태 초기화 (messages, system_mode 등만 사용)
    state = {
        "messages": [],
        "system_mode": "normal",
        "recipe": None,
        "current_step": None
    }

    print("스마트홈 시스템에 오신 것을 환영합니다. '종료'를 입력하면 대화가 끝납니다.")

    while True:
        user_input = input("\n사용자: ")
        if user_input.strip().lower() in ["종료", "quit", "exit"]:
            print("대화를 종료합니다. 감사합니다.")
            break

        # 입력 메시지를 messages에 추가
        state["messages"].append(HumanMessage(content=user_input))
        result = await graph.ainvoke(input=state, config={"callbacks": [langfuse_handler]})
        logger.info(f"결과: {result}")

        # 마지막 content가 비어있지 않은 메시지 찾기
        if "messages" in result and result["messages"]:
            for msg in reversed(result["messages"]):
                if hasattr(msg, "content") and msg.content.strip():
                    print("=" * 50)
                    print(f"시스템: {msg.content}")
                    print("=" * 50)
                    # 대화 이력에 AI 응답도 추가
                    state["messages"].append(msg)
                    break
            else:
                print("시스템: (응답이 없습니다.)")
        else:
            print("시스템: (응답이 없습니다.)")

if __name__ == "__main__":
    asyncio.run(main())