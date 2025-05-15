from typing import Dict, Any
from ..state import AgentState
from langchain_core.messages import AIMessage, HumanMessage

# 이 노드는 LLM을 사용하여 사용자의 의도를 파악하고, 상태를 업데이트합니다.
# 실제로는 LangChain의 LLMChain 등을 사용하여 구현합니다.
async def parse_intent_node(state: AgentState) -> Dict[str, Any]:
    print("---의도 분석 노드 실행---")
    user_message = state["messages"][-1].content
    # TODO: LLM을 사용하여 사용자 메시지로부터 의도, 필요한 정보 추출
    # 예시: "냉장고에 뭐 있어?" -> intent: "query_device_status", device: "refrigerator"
    # 예시: "토마토 파스타 만들어줘" -> intent: "recipe_recommendation_general", query: "토마토 파스타"

    # 임시로 간단한 키워드 기반 의도 분석
    if "냉장고" in user_message and ("뭐 있어" in user_message or "알려줘" in user_message):
        updated_intent = "query_device_status"
        pending_tool_calls = [
            {
                "tool_name": "refrigerator.get_contents",
                "tool_args": {},
                "mcp_client_type": "refrigerator",
            }
        ]
        response_to_user = "냉장고 내용을 확인해볼게요."
        next_node = "execute_tool_call"
    elif "인덕션" in user_message and "꺼줘" in user_message:
        updated_intent = "direct_device_control"
        pending_tool_calls = [
            {
                "tool_name": "induction.turn_off",
                "tool_args": {},
                "mcp_client_type": "induction",
            }
        ]
        response_to_user = "인덕션을 끄겠습니다."
        next_node = "execute_tool_call"
    elif "레시피 추천" in user_message or ("만들만한 거" in user_message and "추천" in user_message):
        updated_intent = "recipe_recommendation_ingredient"
        # TODO: 메시지에서 재료 추출 로직 필요
        response_to_user = "재료 기반 레시피를 추천해 드릴게요. 잠시만요."
        # cooking_mcp를 호출하도록 pending_tool_calls 설정
        pending_tool_calls = [
            {
                "tool_name": "cooking.search_recipes", 
                "tool_args": {"ingredients": state.get("user_provided_ingredients", [])}, # 예시, 실제로는 상태에서 가져와야 함
                "mcp_client_type": "cooking"
            }
        ]
        next_node = "execute_tool_call"
    else:
        updated_intent = "general_chat"
        response_to_user = "죄송합니다, 잘 이해하지 못했어요. 요리 관련해서 도와드릴까요?"
        pending_tool_calls = None
        next_node = None # 일반 채팅은 여기서 종료 또는 다른 노드로

    print(f"사용자 메시지: {user_message}")
    print(f"파악된 의도: {updated_intent}")
    print(f"생성된 MCP 호출: {pending_tool_calls}")

    return {
        "current_intent": updated_intent,
        "pending_tool_calls": pending_tool_calls,
        "response_to_user": AIMessage(content=response_to_user).content if response_to_user else None,
        "next_node_override": next_node
    } 