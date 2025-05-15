from langgraph.graph import StateGraph, END
from utils.state import SmartHomeState
from agents.cooking_subgraph.init_agent import get_init_cooking_agent
from agents.cooking_subgraph.step_agent import get_step_cooking_agent
import asyncio

# 쿠킹 init 노드 (비동기 agent 호출)
async def cooking_init_node(state: SmartHomeState):
    agent = await get_init_cooking_agent()
    return await agent.ainvoke(state)

# 쿠킹 step 노드 (비동기 agent 호출)
async def cooking_step_node(state: SmartHomeState):
    agent = await get_step_cooking_agent()
    return await agent.ainvoke(state)

# 쿠킹 서브그래프 생성 함수
def get_cooking_subgraph():
    sg = StateGraph(SmartHomeState)
    sg.add_node("init", cooking_init_node)
    sg.add_node("step", cooking_step_node)
    sg.add_edge("init", "step")
    sg.add_edge("step", END)
    sg.set_entry_point("init")
    return sg 