# cooking_agent/nodes/ingredient_check_node.py
from langchain_core.messages import AIMessage
from state import State
from utils.logger import setup_logger
from mcp_utils.mcp_client import call_mcp_tool

logger = setup_logger(__name__)

async def ingredient_check_node(state: State) -> State:
    if not state.get("selected_recipe"):
        state["error_message"] = "선택된 레시피가 없습니다."
        return state

    current_step_idx = state.get("current_cooking_step_index", 0)
    cooking_plan = state.get("cooking_plan", [])
    if current_step_idx >= len(cooking_plan):
        state["error_message"] = "요리 단계가 잘못되었습니다."
        return state

    current_step = cooking_plan[current_step_idx]
    required_ingredients = current_step.get("ingredients", [])
    state["required_ingredients_for_current_step"] = required_ingredients

    logger.info("냉장고 MCP에 재료 정보 요청")
    try:
        inventory = await call_mcp_tool(
            mcp_server="refrigerator",
            tool_name="get_contents",
            tool_args={}
        )
        state["inventory"] = inventory
    except Exception as e:
        logger.error(f"냉장고 MCP 호출 실패: {e}")
        state["error_message"] = "냉장고 재료 확인 중 오류가 발생했습니다."
        return state

    missing = [ing for ing in required_ingredients if ing not in inventory]
    state["missing_ingredients"] = missing

    if missing:
        response_text = f"현재 단계에 필요한 재료 중 {', '.join(missing)} 가(이) 부족합니다."
    else:
        response_text = "모든 재료가 준비되어 있습니다."

    state["messages"].append(AIMessage(content=response_text))
    return state
