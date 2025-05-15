# cooking_agent/nodes/supervisor_node.py
from typing import Any
from langchain_core.messages import HumanMessage
from state import State
from utils.logger import setup_logger

logger = setup_logger(__name__)

async def supervisor_node(state: State) -> State:
    messages = state.get("messages", [])
    if not messages or not isinstance(messages[-1], HumanMessage):
        state["error_message"] = "사용자 입력이 필요합니다."
        state["current_intent"] = "other_intent"
        return state

    user_input = messages[-1].content.lower()
    logger.info(f"사용자 입력 분석: {user_input}")

    # 간단한 키워드 기반 의도 분류 예시 (실제론 LLM 호출 권장)
    if any(word in user_input for word in ["요리", "레시피", "만들어"]):
        if state.get("active_flow") == "cooking":
            state["current_intent"] = "continue_cooking_flow"
        else:
            state["current_intent"] = "start_cooking_flow"
            state["recipe_query"] = user_input
    elif any(word in user_input for word in ["꺼줘", "켜줘", "인덕션", "전자레인지", "냉장고"]):
        state["current_intent"] = "direct_device_control"
        # 실제 MCP 호출 정보는 device_control_node에서 결정
    elif any(word in user_input for word in ["테스트 룰", "규칙", "설명"]):
        state["current_intent"] = "general_chat"
    else:
        state["current_intent"] = "general_chat"

    logger.info(f"분석된 의도: {state['current_intent']}")
    return state
