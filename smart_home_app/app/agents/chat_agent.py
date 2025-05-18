import os
import asyncio
import signal
from typing import Dict, List, Any
import contextlib
import aiofiles

from langchain_google_vertexai import ChatVertexAI
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# 환경 변수 로드
load_dotenv()

# 싱글톤 인스턴스
_llm_instance = None
_mcp_client = None
_mcp_tools_cache = None

from langfuse.callback import CallbackHandler
langfuse_handler = CallbackHandler(
    public_key="",
    secret_key="",
    host=""
)
# MCP 서버 URL 설정
MCP_SERVERS = {
    "refrigerator": {
        "url": os.environ.get("REFRIGERATOR_MCP_URL", "http://localhost:10001/sse"),
        "transport": "sse",
    },
    "induction": {
        "url": os.environ.get("INDUCTION_MCP_URL", "http://localhost:10002/sse"),
        "transport": "sse",
    },
    "microwave": {
        "url": os.environ.get("MICROWAVE_MCP_URL", "http://localhost:10003/sse"),
        "transport": "sse",
    },
    "mobile": {
        "url": os.environ.get("MOBILE_MCP_URL", "http://localhost:10004/sse"),
        "transport": "sse",
    },
    "cooking": {
        "url": os.environ.get("COOKING_MCP_URL", "http://localhost:10005/sse"),
        "transport": "sse",
    },
    "personalization": {
        "url": os.environ.get("PERSONALIZATION_MCP_URL", "http://localhost:10006/sse"),
        "transport": "sse",
    },
    "tv": {
        "url": os.environ.get("TV_MCP_URL", "http://localhost:10007/sse"),
        "transport": "sse",
    },
    "audio": {
        "url": os.environ.get("AUDIO_MCP_URL", "http://localhost:10008/sse"),
        "transport": "sse",
    },
    "light": {
        "url": os.environ.get("LIGHT_MCP_URL", "http://localhost:10009/sse"),
        "transport": "sse",
    },
    "curtain": {
        "url": os.environ.get("CURTAIN_MCP_URL", "http://localhost:10010/sse"),
        "transport": "sse",
    },
}

# MCP 클라이언트 초기화 함수
async def init_mcp_client():
    """MCP 클라이언트를 초기화합니다."""
    global _mcp_client
    if _mcp_client is None:
        print("MCP 클라이언트 초기화 시작")
        
        try:
            # MCP 클라이언트 생성
            print("MCP 클라이언트 생성 중...")
            client = MultiServerMCPClient(MCP_SERVERS)
            print("MCP 클라이언트 인스턴스 생성 완료")
            
            # MCP 클라이언트 연결
            print("MCP 서버에 연결 시도 중...")
            await client.__aenter__()
            print("MCP 서버 연결 성공")
            
            _mcp_client = client
            print("MCP 클라이언트 초기화 완료")
        except Exception as e:
            print(f"MCP 클라이언트 초기화 중 오류 발생: {str(e)}")
            if client:
                try:
                    await client.__aexit__(None, None, None)
                except Exception as close_error:
                    print(f"클라이언트 종료 중 오류: {str(close_error)}")
            raise
    
    return _mcp_client

# MCP 클라이언트 종료 함수
async def close_mcp_client():
    """MCP 클라이언트 연결을 안전하게 종료합니다."""
    global _mcp_client
    
    if _mcp_client is not None:
        print("MCP 클라이언트 연결 종료 중...")
        try:
            await _mcp_client.__aexit__(None, None, None)
            print("MCP 클라이언트 연결 종료 완료")
        except Exception as e:
            print(f"MCP 클라이언트 연결 종료 중 오류 발생: {str(e)}")
        finally:
            _mcp_client = None

# MCP 도구 가져오기 함수
async def get_mcp_tools() -> List:
    """MCP 도구를 가져오고 상세 정보를 출력합니다."""
    global _mcp_tools_cache
    
    # 캐시된 도구가 있으면 반환
    if _mcp_tools_cache is not None:
        return _mcp_tools_cache
    
    try:
        client = await init_mcp_client()
        
        print("MCP 도구 가져오는 중...")
        tools = client.get_tools()
        
        # 도구 정보 출력
        print(f"총 {len(tools)}개의 MCP 도구를 가져왔습니다")
        # for i, tool in enumerate(tools, 1):
        #     try:
        #         tool_name = getattr(tool, "name", f"Tool-{i}")
        #         tool_desc = getattr(tool, "description", "설명 없음")
        #         # print(f"  도구 {i}: {tool_name} - {tool_desc}")
        #     except Exception as e:
        #         print(f"  도구 {i}의 정보를 가져오는 중 오류: {str(e)}")
        
        # 캐시에 저장
        _mcp_tools_cache = tools
        return tools
    except Exception as e:
        print(f"도구 가져오기 중 오류 발생: {str(e)}")
        # 오류 발생 시 빈 목록 반환
        return []

# MCP 도구 정보 변환 함수
async def convert_mcp_tools_to_info() -> List[Dict[str, Any]]:
    """MCP 도구를 사용자 친화적인 형식으로 변환합니다."""
    tools = await get_mcp_tools()
    tools_info = []
    
    for tool in tools:
        try:
            tool_info = {
                "name": getattr(tool, "name", "Unknown"),
                "description": getattr(tool, "description", "설명 없음"),
                "parameters": []
            }
            
            # 파라미터 정보 추출
            if hasattr(tool, "args_schema") and tool.args_schema is not None:
                schema_props = getattr(tool.args_schema, "schema", {}).get("properties", {})
                if schema_props:
                    tool_info["parameters"] = list(schema_props.keys())
            
            tools_info.append(tool_info)
        except Exception as e:
            print(f"도구 정보 변환 중 오류: {str(e)}")
    
    return tools_info

# LLM 모델 초기화 함수
async def get_llm():
    """LLM 모델을 초기화하고 반환합니다."""
    global _llm_instance
    
    if _llm_instance is None:
        # 모델 설정 가져오기
        model_name = os.environ.get("VERTEX_MODEL", "gemini-2.0-flash")
        print(f"LLM 모델 초기화: {model_name}")
        
        _llm_instance = ChatVertexAI(
            model=model_name,
            temperature=0.1,
            max_output_tokens=8190
        )
    
    return _llm_instance

# 프롬프트 생성 함수s
async def generate_prompt() -> str:
    """사용자 요청에 따른 프롬프트를 생성합니다."""
    # 도구 정보 가져오기 시도
    try:
        # 도구 정보 가져오기 (MCP 서버에서 동적으로)
        tools_info = await convert_mcp_tools_to_info()
        
        # 도구 정보 포맷팅
        tools_text = "\n".join([
            f"{i+1}. {tool['name']}: {tool['description']}" 
            for i, tool in enumerate(tools_info)
        ])
        
        if not tools_text:
            tools_text = "현재 사용 가능한 도구가 없습니다. MCP 서버 연결을 확인하세요."
            
    except Exception as e:
        print(f"도구 정보 가져오기 중 오류 발생: {str(e)}")
        tools_text = "도구 정보를 가져오는 중 오류가 발생했습니다. MCP 서버 연결을 확인하세요."
    
    # 프롬프트 파일에서 템플릿 읽기
    prompt_path = os.path.join(os.path.dirname(__file__), '../prompts/react_agent_prompt.txt')
    async with aiofiles.open(prompt_path, mode='r', encoding='utf-8') as f:
        prompt_template = await f.read()
    
    # 프롬프트 완성
    prompt = prompt_template.format(tools=tools_text)

    # print(f"생성된 프롬프트 : {prompt}")    

    return f"{prompt}"

# 계획 생성 함수
async def get_chat_agent() -> str:
    """사용자 요청에 대한 계획을 생성합니다."""
    global _agent_instance
    

    # 프롬프트 생성
    prompt = await generate_prompt()
    print(f"생성된 프롬프트 : {prompt}")
    system_prompt = ChatPromptTemplate.from_messages([
            ("system", prompt),
            MessagesPlaceholder(variable_name="messages")
        ])
    # LLM 모델 가져오기
    llm = await get_llm()

    tools = await get_mcp_tools()

    _agent_instance = create_react_agent(
            llm, 
            tools, 
            prompt=system_prompt,
            debug=True  # 디버그 모드 활성화
        )

    
    return _agent_instance
