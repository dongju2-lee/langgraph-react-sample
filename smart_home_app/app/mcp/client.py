from langchain_mcp_adapters.client import MultiServerMCPClient
from .config import MCP_CONFIG

_mcp_client = None

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
