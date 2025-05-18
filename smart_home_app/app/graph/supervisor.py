from langgraph.graph import StateGraph, END, START
from utils.state import SmartHomeState
from agents.chat_agent import get_chat_agent
from .subgraphs import get_cooking_subgraph
import asyncio
import logging

logger = logging.getLogger("supervisor")
logging.basicConfig(level=logging.INFO)


# 라우터 노드: dict 반환, 'next' 키에 다음 노드 id를 명시해야 함
def router_node(state: SmartHomeState):
    messages = state.get("messages", [])
    logger.info(f"================ super : {messages} ================")
    user_input = messages[-1].content if messages else ""
    if any(word in user_input for word in ["요리", "쿠킹", "레시피"]):
        state["system_mode"] = "cooking"
        logger.info(f"================ super state : {state} ================")
        return {"next": "cooking"}  # 딕셔너리의 키만 반환
    else:
        state["system_mode"] = "normal"
        logger.info(f"================ super state : {state} ================")
        return {"next": "chat"}  # 딕셔너리의 키만 반환


# def router_node(state: SmartHomeState):
#     messages = state.get("messages", [])
#     logger.info(f"================ super : {messages} ================")
#     user_input = messages[-1].content if messages else ""
#     if any(word in user_input for word in ["요리", "쿠킹", "레시피"]):
#         state["system_mode"] = "cooking"
#         logger.info(f"================ super state : {state} ================")
#         return {**state, "next": "cooking"}
#     else:
#         state["system_mode"] = "normal"
#         logger.info(f"================ super state : {state} ================")
#         return {**state, "next": "chat"}

# chat 노드 (비동기 agent 호출)
async def chat_node(state: SmartHomeState):
    agent = await get_chat_agent()
    logger.info(f"================ chat_node state {state}================")
    return await agent.ainvoke(state)

# cooking 서브그래프 노드 (비동기 agent 호출)
async def cooking_node(state: SmartHomeState):
    subgraph = get_cooking_subgraph().compile()
    logger.info(f"================ cooking_node state {state}================")
    return await subgraph.ainvoke(state)

def build_supervisor_graph():
    sg = StateGraph(SmartHomeState)
    sg.add_node("router", router_node)
    sg.add_node("chat", chat_node)
    sg.add_node("cooking", cooking_node)

    sg.add_edge(START,"router")

    sg.add_conditional_edges("router", lambda state: state["next"], {"cooking": "cooking", "chat": "chat"})

    # sg.add_conditional_edges("router", router_node, {"cooking": "cooking", "chat": "chat"})

    # sg.add_edge("router","chat")
    sg.add_edge("chat", END)
    sg.add_edge("cooking", END)
    # sg.add_node("router", router_node)
    # sg.add_node("chat", chat_node)
    # sg.add_node("cooking", cooking_node)


    # sg.add_edge("router", "chat")
    # sg.add_edge("router", "cooking")
    # sg.add_edge("chat", END)
    # sg.add_edge("cooking", END)
    # sg.set_entry_point("router")
    return sg 