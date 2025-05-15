# cooking_agent/nodes/handle_other_node.py
from langchain_core.messages import AIMessage
from state import State
from utils.logger import setup_logger

logger = setup_logger(__name__)

async def handle_other_node(state: State) -> State:
    error_msg = state.get("error_message")
    if error_msg:
        response_text = f"오류가 발생했습니다: {error_msg}"
        state["error_message"] = None
    else:
        response_text = "죄송합니다, 이해하지 못했습니다. 다시 말씀해 주세요."

    state["messages"].append(AIMessage(content=response_text))
    return state
