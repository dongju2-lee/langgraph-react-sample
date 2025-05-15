from langgraph.graph import StateGraph, START, END
from workflow.state import PlanExecuteState
from agents.prompts import PLANNER_PROMPT
from agents.react_agent import get_react_agent
from langchain_core.messages import HumanMessage
from langchain_google_vertexai import ChatVertexAI
import os

planner_llm = ChatVertexAI(model=os.environ.get("PLANNER_MODEL", "gemini-2.5-pro-exp-03-25"), temperature=0.2)

async def plan_node(state):
    user_input = state["input"]
    messages = [HumanMessage(content=user_input)]
    prompt = PLANNER_PROMPT.format(messages=messages)
    plan = await planner_llm.ainvoke(prompt)
    steps = [line.split('. ', 1)[-1] for line in plan.content.split('\n') if line.strip()]
    return {
        **state,
        "plan": steps,
        "current_step": 0,
        "past_steps": [],
        "response": None,
        "messages": messages + [plan]
    }

async def execute_node(state):
    plan = state["plan"]
    idx = state["current_step"]
    past_steps = state.get("past_steps", [])
    if idx >= len(plan):
        return {
            **state,
            "response": "요리가 모두 끝났어요! 수고하셨습니다.",
            "messages": state["messages"] + [HumanMessage(content="요리가 모두 끝났어요! 수고하셨습니다.")]
        }
    agent = await get_react_agent()
    step_instruction = plan[idx]
    plan_str = "\n".join(f"{i+1}. {s}" for i, s in enumerate(plan))
    task_prompt = f"""전체 플랜:
{plan_str}

현재 단계({idx+1}): {step_instruction}

이 단계를 실행하세요. 재료가 없거나 문제가 있으면 반드시 사용자에게 물어보고, 대체재를 제안하거나, 진행/취소 여부를 확인하세요."""
    result = await agent.ainvoke({"messages": state["messages"] + [HumanMessage(content=task_prompt)]})
    return {
        **state,
        "current_step": idx + 1,
        "past_steps": past_steps + [(step_instruction, result["messages"][-1].content)],
        "messages": state["messages"] + [result["messages"][-1]]
    }

def should_end(state: PlanExecuteState):
    return END if state.get("response") else "executor"

def get_workflow():
    builder = StateGraph(PlanExecuteState)
    builder.add_node("planner", plan_node)
    builder.add_node("executor", execute_node)
    builder.add_edge(START, "planner")
    builder.add_edge("planner", "executor")
    builder.add_conditional_edges("executor", should_end, ["executor", END])
    return builder.compile()
