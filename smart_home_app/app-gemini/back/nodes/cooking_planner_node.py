# cooking_agent/nodes/cooking_planner_node.py
from langchain_core.messages import AIMessage
from state import State
from utils.logger import setup_logger
from mcp_utils.mcp_client import call_mcp_tool

logger = setup_logger(__name__)

async def cooking_planner_node(state: State) -> State:
    query = state.get("recipe_query", "")
    if not query:
        state["error_message"] = "레시피 검색어가 없습니다."
        return state

    logger.info(f"쿠킹 MCP에 레시피 검색 요청: {query}")
    try:
        recipes = await call_mcp_tool(
            mcp_server="cooking",
            tool_name="search_recipes",
            tool_args={"query": query}
        )
        state["available_recipes"] = recipes
        # 간단히 첫 번째 레시피 자동 선택 (실제론 사용자 선택 대기 필요)
        if recipes:
            state["selected_recipe_index"] = 0
            state["selected_recipe"] = recipes[0]
            # 요리 계획 생성 (예시: MCP에서 단계별 지침 받음)
            plan = await call_mcp_tool(
                mcp_server="cooking",
                tool_name="get_recipe_steps",
                tool_args={"recipe_id": recipes[0]["id"]}
            )
            state["cooking_plan"] = plan
            state["current_cooking_step_index"] = 0
            state["active_flow"] = "cooking"
            response_text = f"'{recipes[0]['name']}' 레시피를 선택했습니다. 요리를 시작할까요?"
        else:
            response_text = "조건에 맞는 레시피를 찾지 못했습니다."
    except Exception as e:
        logger.error(f"쿠킹 MCP 호출 실패: {e}")
        response_text = "레시피 검색 중 오류가 발생했습니다."

    state["messages"].append(AIMessage(content=response_text))
    return state
