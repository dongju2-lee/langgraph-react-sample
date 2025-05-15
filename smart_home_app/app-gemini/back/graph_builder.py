# cooking_agent/graph_builder.py
import os
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.messages import AIMessage

from .state import AgentState
from .nodes import (
    supervisor_node,
    general_chat_node,
    cooking_planner_node,
    ingredient_check_node,
    replanning_or_guidance_node,
    execute_cooking_step_node,
    final_cooking_summary_node,
    handle_other_node,
    parse_intent_node,
    execute_tool_node
)
from .utils.logger import setup_logger
import logging

logger = logging.getLogger(__name__)

# --- 체크포인터 설정 (main.py에서 DB 경로를 주입받거나 여기서 직접 설정) ---
# 여기서는 DB 경로를 직접 설정하는 예시
db_path = os.path.join(os.path.dirname(__file__), "langgraph_cooking_agent.sqlite")
memory = SqliteSaver.from_conn_string(db_path)
logger.info(f"LangGraph 체크포인터 DB 경로 (graph_builder): {db_path}")

def create_cooking_agent_graph():
    logger.info("쿠킹 에이전트 그래프 생성 시작 (from graph_builder.py)")
    builder = StateGraph(AgentState)

    # --- 노드 추가 ---
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("general_chat", general_chat_node)
    builder.add_node("parse_intent", parse_intent_node)
    builder.add_node("execute_tool_call", execute_tool_node)
    builder.add_node("cooking_planner", cooking_planner_node)
    builder.add_node("ingredient_check", ingredient_check_node)
    builder.add_node("replanning_or_guidance", replanning_or_guidance_node)
    builder.add_node("execute_cooking_step", execute_cooking_step_node)
    builder.add_node("final_cooking_summary", final_cooking_summary_node)
    builder.add_node("handle_other", handle_other_node)

    # --- 진입점 설정 ---
    builder.set_entry_point("supervisor")

    # --- 엣지 정의 (조건부 라우팅) ---
    def route_from_supervisor(state: AgentState):
        intent = state.get("current_intent")
        logger.debug(f"Supervisor 라우팅: 의도='{intent}'")

        if state.get("error_message"):
            state["error_message"] = None
            return "handle_other"

        if intent == "general_chat":
            return "general_chat"
        elif intent in ["query_device_status", "direct_device_control", "recipe_recommendation_ingredient", "recipe_recommendation_general", "send_message_request"]:
            return "parse_intent"
        elif intent == "start_cooking_flow":
            return "cooking_planner"
        elif intent == "continue_cooking_flow" and state.get("active_flow") == "cooking":
            return "execute_cooking_step"
        elif intent in ["ask_for_recipe_selection", "ask_for_replan_confirmation", "ask_for_step_confirmation"]:
            logger.info(f"사용자 확인/선택 대기 상태 ({intent}). Supervisor에서 END로 라우팅.")
            return END
        else:
            logger.warning(f"Supervisor에서 분류되지 않은 의도 '{intent}'. parse_intent로 전달.")
            return "parse_intent"

    builder.add_conditional_edges(
        "supervisor",
        route_from_supervisor,
        {
            "general_chat": "general_chat",
            "parse_intent": "parse_intent",
            "cooking_planner": "cooking_planner",
            "execute_cooking_step": "execute_cooking_step",
            "handle_other": "handle_other",
            END: END
        }
    )

    builder.add_edge("general_chat", END)
    builder.add_edge("handle_other", END)
    builder.add_edge("cooking_planner", "ingredient_check")
    builder.add_edge("ingredient_check", "replanning_or_guidance")
    builder.add_edge("replanning_or_guidance", END)

    def route_after_execute_step(state: AgentState):
        logger.debug("ExecuteCookingStep 라우팅 결정")
        if state.get("error_message"): return "handle_other"
        
        next_node_override = state.get("next_node_override")
        if next_node_override:
            logger.debug(f"다음 노드 오버라이드: {next_node_override}")
            return next_node_override
        
        active_flow = state.get("active_flow")
        if active_flow != "cooking":
            logger.debug("요리 흐름이 아님. Supervisor로 이동.")
            return "supervisor"

        current_idx = state.get("current_cooking_step_index")
        cooking_plan = state.get("cooking_plan", [])
        plan_length = len(cooking_plan)

        if current_idx is not None and cooking_plan and current_idx >= plan_length:
            logger.debug("모든 요리 단계 완료. 최종 요약으로 이동.")
            return "final_cooking_summary"
        
        if state.get("response_to_user") and state.get("current_intent") == "ask_for_step_confirmation":
             logger.debug("사용자 단계 완료 확인 대기 (ask_for_step_confirmation). END로 라우팅.")
             return END

        logger.debug("다음 요리 단계 실행으로 이동.")
        return "execute_cooking_step"

    builder.add_conditional_edges(
        "execute_cooking_step",
        route_after_execute_step,
        {
            "final_cooking_summary": "final_cooking_summary",
            "execute_cooking_step": "execute_cooking_step",
            "ingredient_check": "ingredient_check",
            "supervisor": "supervisor",
            "handle_other": "handle_other",
            END: END
        }
    )

    builder.add_edge("final_cooking_summary", END)

    # 1. 의도 분석 후 다음 행동 결정
    def decide_after_intent_parsing(state: AgentState):
        logger.debug(f"Intent Parsing 후 라우팅: next_node_override='{state.get('next_node_override')}', pending_tools='{bool(state.get('pending_tool_calls'))}'")
        next_node = state.get("next_node_override")
        if next_node:
            return next_node
        if state.get("pending_tool_calls"):
            return "execute_tool_call"
        if state.get("response_to_user"):
            logger.info("도구 호출 없이 사용자에게 바로 응답. END로 라우팅.")
            return END
        return END

    builder.add_conditional_edges(
        "parse_intent",
        decide_after_intent_parsing,
        {
            "execute_tool_call": "execute_tool_call",
            END: END
        }
    )

    # 2. MCP 도구 실행 후 다음 행동 결정
    def decide_after_tool_execution(state: AgentState):
        logger.debug(f"Tool Execution 후 라우팅: tool_results='{state.get('tool_call_results')}'")
        tool_results = state.get("tool_call_results")
        if tool_results:
            first_res = tool_results[0]
            if first_res.get("error"):
                response_content = f"도구 '{first_res.get('tool_name')}' 실행 중 오류: {first_res.get('error')}"
            elif first_res.get("result") is not None:
                response_content = f"'{first_res.get('tool_name')}' 실행 결과: {str(first_res.get('result'))[:200]}"
                if len(str(first_res.get('result'))) > 200: response_content += "..."
            else:
                response_content = f"'{first_res.get('tool_name')}' 실행 완료."
            
            state["response_to_user"] = response_content
            if state.get("messages"):
                state["messages"].append(AIMessage(content=response_content))
            else:
                state["messages"] = [AIMessage(content=response_content)]
            logger.info(f"도구 실행 결과 기반 응답: {response_content}")
            return END
        
        logger.warning("도구 실행 후 처리 로직에서 명확한 응답 생성 안됨. Supervisor로 복귀.")
        return "supervisor"

    builder.add_conditional_edges(
        "execute_tool_call",
        decide_after_tool_execution,
        {
            "supervisor": "supervisor",
            END: END
        }
    )

    # 그래프 컴파일 (체크포인터 포함)
    graph = builder.compile(checkpointer=memory)
    logger.info("쿠킹 에이전트 그래프 생성 완료 (from graph_builder.py)")
    return graph

# 이 파일을 직접 실행할 경우를 위한 테스트 코드 (선택 사항)
if __name__ == "__main__":
    logger.info("graph_builder.py를 직접 실행하여 그래프 객체를 테스트합니다.")
    # 로깅 설정 (main.py와 유사하게)
    import logging as py_logging # 충돌 방지
    py_logging.basicConfig(level=os.environ.get("LOG_LEVEL", "DEBUG").upper(), format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    test_graph = create_cooking_agent_graph()
    if test_graph:
        logger.info("테스트 그래프 객체가 성공적으로 생성되었습니다.")
        # Mermaid 다이어그램 출력 (디버깅용)
        try:
            mermaid_diagram = test_graph.get_graph().draw_mermaid()
            logger.info("생성된 그래프의 Mermaid 다이어그램:\n" + mermaid_diagram)
        except Exception as e:
            logger.error(f"Mermaid 다이어그램 생성 중 오류: {e}")
    else:
        logger.error("테스트 그래프 객체 생성에 실패했습니다.")
