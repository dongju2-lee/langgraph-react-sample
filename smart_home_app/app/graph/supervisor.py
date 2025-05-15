from langgraph.graph import StateGraph, END
from utils.state import SmartHomeState
from agents.chat_agent import get_chat_agent
from .subgraphs import get_cooking_subgraph
import asyncio

# 라우터 노드: dict 반환, 'next' 키에 다음 노드 id를 명시해야 함
def router_node(state: SmartHomeState):
    messages = state.get("messages", [])
    user_input = messages[-1].content if messages else ""
    if any(word in user_input for word in ["요리", "쿠킹", "레시피"]):
        state["system_mode"] = "cooking"
        return {**state, "next": "cooking"}
    else:
        state["system_mode"] = "normal"
        return {**state, "next": "chat"}

# chat 노드 (비동기 agent 호출)
async def chat_node(state: SmartHomeState):
    agent = await get_chat_agent()
    return await agent.ainvoke(state)

# cooking 서브그래프 노드 (비동기 agent 호출)
async def cooking_node(state: SmartHomeState):
    subgraph = get_cooking_subgraph().compile()
    return await subgraph.ainvoke(state)

def build_supervisor_graph():
    sg = StateGraph(SmartHomeState)
    sg.add_node("router", router_node)
    sg.add_node("chat", chat_node)
    sg.add_node("cooking", cooking_node)
    sg.add_edge("router", "chat")
    sg.add_edge("router", "cooking")
    sg.add_edge("chat", END)
    sg.add_edge("cooking", END)
    sg.set_entry_point("router")
    return sg 