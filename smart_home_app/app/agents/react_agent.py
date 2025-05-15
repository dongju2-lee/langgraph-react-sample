import os
from langchain_google_vertexai import ChatVertexAI
from langgraph.prebuilt import create_react_agent
from .prompts import REACT_SYSTEM_PROMPT
from langchain_mcp_adapters.client import MultiServerMCPClient

_mcp_client = None

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



async def get_mcp_client():
    global _mcp_client
    if _mcp_client is None:
        client = MultiServerMCPClient(MCP_CONFIG)
        await client.__aenter__()
        _mcp_client = client
    return _mcp_client

async def get_all_tools():
    client = await get_mcp_client()
    return client.get_tools()

_agent = None

async def get_react_agent():
    global _agent
    if _agent is None:
        llm = ChatVertexAI(model=os.environ.get("REACT_MODEL", "gemini-2.5-pro-exp-03-25"), temperature=0.2)
        tools = await get_all_tools()
        _agent = create_react_agent(
            llm,
            tools,
            prompt=REACT_SYSTEM_PROMPT,
            debug=True
        )
    return _agent
