# cooking_agent/nodes/device_control_node.py
from typing import List
from langchain_core.messages import AIMessage
from state import State, ToolCall
from utils.logger import setup_logger
from mcp_utils.mcp_client import call_mcp_tool  # MCP 호출 래퍼 함수

logger = setup_logger(__name__)

async def device_control_node(state: State) -> State:
    pending_calls: List[ToolCall] = state.get("pending_mcp_calls", [])
    if not pending_calls:
        state["error_message"] = "실행할 MCP 명령이 없습니다."
        return state

    results = []
    for call in pending_calls:
        try:
            logger.info(f"MCP 호출: 서버={call['mcp_server_name']}, 도구={call['tool_name']}, 인자={call['tool_args']}")
            result = await call_mcp_tool(
                mcp_server=call["mcp_server_name"],
                tool_name=call["tool_name"],
                tool_args=call["tool_args"]
            )
            results.append(result)
        except Exception as e:
            logger.error(f"MCP 호출 실패: {e}")
            results.append({"error": str(e)})

    state["mcp_call_results"] = results
    state["pending_mcp_calls"] = []  # 호출 후 초기화

    # 결과를 간단히 요약해 사용자에게 알림
    response_text = "장치 제어를 완료했습니다."
    if any("error" in r for r in results):
        response_text = "일부 장치 제어에 실패했습니다."

    from langchain_core.messages import AIMessage
    state["messages"].append(AIMessage(content=response_text))
    return state
