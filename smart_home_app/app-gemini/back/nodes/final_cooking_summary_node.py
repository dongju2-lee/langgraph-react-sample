# cooking_agent/nodes/final_cooking_summary_node.py
from langchain_core.messages import AIMessage
from state import State
from utils.logger import setup_logger

logger = setup_logger(__name__)

async def final_cooking_summary_node(state: State) -> State:
    recipe = state.get("selected_recipe", {})
    recipe_name = recipe.get("name", "요리")

    response_text = f"{recipe_name} 요리가 완료되었습니다! 맛있게 드세요 :)"
    state["messages"].append(AIMessage(content=response_text))
    state["active_flow"] = "none"
    state["current_cooking_step_index"] = None
    state["cooking_plan"] = None
    return state
