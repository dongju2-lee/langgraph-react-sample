# cooking_agent/nodes/general_chat_node.py
from langchain_core.messages import AIMessage
from state import State
from utils.logger import setup_logger
from langchain_google_vertexai import ChatVertexAI

logger = setup_logger(__name__)

async def general_chat_node(state: State) -> State:
    messages = state.get("messages", [])
    if not messages:
        state["error_message"] = "대화 기록이 없습니다."
        return state

    llm = ChatVertexAI(model="gemini-1.5-pro-preview-0409", temperature=0.7)

    # LLM에 전달할 프롬프트: 이전 대화 전체 전달
    # 실제로는 프롬프트 템플릿을 분리해 관리하는 것이 좋음
    prompt_messages = messages

    logger.info("일상 대화용 LLM 호출 시작")
    response = await llm.achat(prompt_messages)
    logger.info("일상 대화용 LLM 호출 완료")

    ai_msg = AIMessage(content=response.content)
    state["messages"].append(ai_msg)
    return state
