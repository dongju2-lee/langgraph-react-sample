import os
import logging
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_google_vertexai import ChatVertexAI
from langgraph.prebuilt import create_react_agent

logger = logging.getLogger("chat_agent")
logging.basicConfig(level=logging.INFO)

MCP_CONFIG = {
    "refrigerator": {
        "url": os.environ.get("REFRIGERATOR_MCP_URL", "http://localhost:8001/sse"),
        "transport": "sse",
    },
    "induction": {
        "url": os.environ.get("INDUCTION_MCP_URL", "http://localhost:8002/sse"),
        "transport": "sse",
    },
    "microwave": {
        "url": os.environ.get("MICROWAVE_MCP_URL", "http://localhost:8003/sse"),
        "transport": "sse",
    },
    "mobile": {
        "url": os.environ.get("MOBILE_MCP_URL", "http://localhost:8004/sse"),
        "transport": "sse",
    },
    "cooking": {
        "url": os.environ.get("COOKING_MCP_URL", "http://localhost:8005/sse"),
        "transport": "sse",
    },
}

def build_tools_info_text(tools):
    logger.info(f"MCP 도구 {len(tools)}개 정보 변환 시작")
    lines = []
    for i, tool in enumerate(tools, 1):
        name = getattr(tool, "name", f"Tool-{i}")
        desc = getattr(tool, "description", "설명 없음")
        params = []
        if hasattr(tool, "args_schema") and tool.args_schema is not None:
            schema_props = getattr(tool.args_schema, "schema", {}).get("properties", {})
            if schema_props:
                params = list(schema_props.keys())
        param_str = ", ".join(params) if params else "없음"
        lines.append(f"{i}. {name}: {desc} (파라미터: {param_str})")
        logger.info(f"도구 {i}: {name} - {desc} (파라미터: {param_str})")
    if not lines:
        logger.warning("MCP에서 사용 가능한 도구가 없습니다.")
    return "\n".join(lines) if lines else "현재 사용 가능한 도구가 없습니다."

def make_dynamic_prompt(tools):
    logger.info("동적 system 프롬프트 생성 시작")
    tools_info = build_tools_info_text(tools)
    SYSTEM_PROMPT = f"""당신은 스마트홈 시스템의 챗봇 에이전트입니다.\n아래는 현재 연결된 MCP 도구 목록입니다:\n\n{tools_info}\n\n사용자의 요청에 따라 적절한 도구를 선택해 작업을 수행하세요.\n"""
    logger.info("동적 system 프롬프트 생성 완료")
    def prompt(state):
        return [
            {"role": "system", "content": SYSTEM_PROMPT},
            *state["messages"]
        ]
    return prompt

async def get_chat_agent():
    logger.info("MCP 클라이언트 연결 및 도구 정보 수집 시작")
    async with MultiServerMCPClient(MCP_CONFIG) as client:
        tools = client.get_tools()
        logger.info(f"MCP 도구 {len(tools)}개 수집 완료")
        llm = ChatVertexAI(model="gemini-2.0-flash", temperature=0.1, max_output_tokens=2048)
        logger.info("LLM 인스턴스 생성 완료")
        prompt = make_dynamic_prompt(tools)
        agent = create_react_agent(model=llm, tools=tools, prompt=prompt)
        logger.info("ReAct 에이전트 생성 완료")
        return agent
