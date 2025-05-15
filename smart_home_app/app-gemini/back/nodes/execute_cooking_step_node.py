# cooking_agent/nodes/execute_cooking_step_node.py
from langchain_core.messages import AIMessage
from state import State, ToolCall
from utils.logger import setup_logger

logger = setup_logger(__name__)

async def execute_cooking_step_node(state: State) -> State:
    current_idx = state.get("current_cooking_step_index", 0)
    plan = state.get("cooking_plan", [])

    if current_idx >= len(plan):
        state["error_message"] = "요리 단계가 잘못되었습니다."
        return state

    step = plan[current_idx]
    instruction = step.get("instruction", "다음 단계를 진행하세요.")
    mcp_needed = step.get("mcp_needed")
    mcp_tool = step.get("mcp_tool")
    mcp_args = step.get("mcp_args", {})

    response_text = instruction
    pending_calls = []

    if mcp_needed and mcp_tool:
        pending_calls.append(ToolCall(
            mcp_server_name=mcp_needed,
            tool_name=mcp_tool,
            tool_args=mcp_args
        ))
        response_text += f" (장치를 제어합니다: {mcp_needed})"

    state["pending_mcp_calls"] = pending_calls
    state["messages"].append(AIMessage(content=response_text))

    # 다음 단계 인덱스 증가 (필요시 사용자 확인 후 증가하도록 변경 가능)
    state["current_cooking_step_index"] = current_idx + 1

    return state
