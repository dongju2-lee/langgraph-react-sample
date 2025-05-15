# cooking_agent/nodes/replanning_or_guidance_node.py
from langchain_core.messages import AIMessage
from state import State
from utils.logger import setup_logger
from mcp_utils.mcp_client import call_mcp_tool

logger = setup_logger(__name__)

async def replanning_or_guidance_node(state: State) -> State:
    missing = state.get("missing_ingredients", [])
    if missing:
        logger.info(f"대체 재료 추천 요청: {missing}")
        try:
            suggestion = await call_mcp_tool(
                mcp_server="cooking",
                tool_name="suggest_alternatives",
                tool_args={"missing_ingredients": missing}
            )
            state["alternative_ingredients_suggestion"] = suggestion
            response_text = f"부족한 재료를 대체할 수 있는 제안입니다: {suggestion}. 계속 진행할까요?"
        except Exception as e:
            logger.error(f"대체 재료 추천 실패: {e}")
            response_text = "대체 재료 추천 중 오류가 발생했습니다. 계속 진행할까요?"
    else:
        response_text = "재료가 모두 준비되어 있습니다. 다음 단계로 진행합니다."

    state["messages"].append(AIMessage(content=response_text))
    return state
