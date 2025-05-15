from typing import Dict, Any, List
from ..state import AgentState, ToolCall
from ..mcp_utils.adapters import BaseMCPAdapter # MCPClients를 직접 사용하기보다, 여기서 필요에 따라 가져오는 방식

# 이 노드는 AgentState에 있는 pending_tool_calls를 실행합니다.
async def execute_tool_node(state: AgentState) -> Dict[str, Any]:
    print("---MCP 도구 실행 노드---")
    pending_calls: List[ToolCall] = state.get("pending_tool_calls")
    mcp_clients = state.get("mcp_clients") # main.py 등에서 미리 초기화되어 상태에 주입됨
    tool_call_results = []
    
    if not pending_calls or not mcp_clients:
        print("실행할 MCP 호출 또는 MCP 클라이언트가 없습니다.")
        return {"tool_call_results": [], "pending_tool_calls": []}

    for call_info in pending_calls:
        tool_name = call_info["tool_name"]
        tool_args = call_info["tool_args"]
        mcp_client_type = call_info["mcp_client_type"]
        result = None
        error_message = None

        print(f">>> MCP 호출 실행: {tool_name}({tool_args}) on {mcp_client_type}")

        client: BaseMCPAdapter = mcp_clients.get(mcp_client_type)
        if not client:
            error_message = f"{mcp_client_type} 클라이언트를 찾을 수 없습니다."
            print(error_message)
            tool_call_results.append({"tool_name": tool_name, "error": error_message})
            continue
        
        try:
            # tool_name을 기반으로 실제 어댑터의 메서드를 동적으로 호출
            # 예: tool_name "refrigerator.get_contents" -> client.get_contents()
            # tool_name "induction.set_power" -> client.set_power(**tool_args)
            action_name = tool_name.split(".")[1] # "get_contents", "set_power" 등
            if hasattr(client, action_name):
                method_to_call = getattr(client, action_name)
                if tool_args:
                    result = await method_to_call(**tool_args)
                else:
                    result = await method_to_call()
                print(f"MCP 호출 결과 ({tool_name}): {result}")
            else:
                error_message = f"{mcp_client_type} 클라이언트에 {action_name} 메서드가 없습니다."
                print(error_message)
        except Exception as e:
            error_message = f"{tool_name} 실행 중 오류: {str(e)}"
            print(error_message)
        
        tool_call_results.append({
            "tool_name": tool_name,
            "args": tool_args,
            "result": result,
            "error": error_message
        })

    # 실행된 호출은 비워줍니다.
    return {"tool_call_results": tool_call_results, "pending_tool_calls": [], "response_to_user": None} # 결과는 다음 노드에서 처리하여 응답 생성 