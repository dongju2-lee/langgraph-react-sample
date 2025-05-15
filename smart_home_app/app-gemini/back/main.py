# cooking_agent/main.py
import asyncio
import os
import json
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage
import uuid
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Tuple

# --- .env 파일 로드 ---
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
    print(f".env 파일 로드 성공: {dotenv_path}")
else:
    print(f"경고: .env 파일을 찾을 수 없습니다 ({dotenv_path}). 환경 변수가 제대로 로드되지 않을 수 있습니다.")

# --- 로거 설정 (utils.logger.py 사용 권장) ---
import logging # 임시 로거
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=LOG_LEVEL, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
# from .utils.logger import setup_logger # utils.logger.py를 만들었다면 이렇게 사용
# logger = setup_logger(__name__)

# --- 그래프 빌더 임포트 ---
from .graph_builder import create_cooking_agent_graph, memory as graph_memory

# --- MCP 설정 (여전히 main.py 또는 별도 config.py에서 관리 가능) ---
MCP_BASE_URL = os.environ.get("MCP_BASE_URL", "http://localhost")
MCP_CONFIG = {
    "refrigerator": {"url": f"{MCP_BASE_URL}:{os.environ.get('REFRIGERATOR_MCP_PORT', '8001')}/sse", "transport": "sse"},
    "induction": {"url": f"{MCP_BASE_URL}:{os.environ.get('INDUCTION_MCP_PORT', '8002')}/sse", "transport": "sse"},
    # ... (나머지 MCP 설정 동일하게)
}
logger.info(f"MCP 설정 로드 완료 (main.py): {json.dumps(MCP_CONFIG, indent=2)}")

# --- 기타 임포트 ---
from .state import AgentState, MCPClients # AgentState 사용
from .mcp_utils import get_mcp_clients # MCP 클라이언트 초기화 함수

# FastAPI 앱 생성
app = FastAPI(
    title="Smart Home Cooking Agent API",
    description="LangGraph 기반 쿠킹 에이전트 API",
    version="0.1.0"
)

# CORS 설정 (React 등 프론트엔드와 통신 시 필요)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 배포 시에는 특정 도메인만 허용하세요.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# LangGraph 애플리케이션 인스턴스 생성
# 이 시점에서 DB 파일이 없다면 생성됩니다.
langgraph_app = create_cooking_agent_graph()
logger.info("LangGraph 애플리케이션 인스턴스 생성 완료.")

# MCP 클라이언트 초기화 (애플리케이션 시작 시 한 번만)
mcp_clients_instance: Optional[MCPClients] = None

@app.on_event("startup")
async def startup_event():
    global mcp_clients_instance
    logger.info("애플리케이션 시작 이벤트: MCP 클라이언트 초기화 시도")
    mcp_clients_instance = await get_mcp_clients()
    if mcp_clients_instance:
        logger.info("MCP 클라이언트 초기화 완료.")
        for name, client in mcp_clients_instance.items():
            if client: 
                logger.info(f"  - {name} 클라이언트 로드됨 (URL: {client.base_url})")
            else:
                logger.warning(f"  - {name} 클라이언트 URL이 .env에 설정되지 않아 로드되지 않음")
    else:
        logger.error("MCP 클라이언트 초기화 실패.")

# --- 요청 및 응답 모델 정의 ---
class ChatInput(BaseModel):
    conversation_id: Optional[str] = Field(None, description="기존 대화 ID, 없으면 새로 생성")
    message: str = Field(..., description="사용자 메시지")
    # 추가적인 컨텍스트 정보를 받을 수 있음 (예: 현재 앱 상태, 사용자 설정 등)
    # current_ingredients: Optional[List[str]] = None 

class ChatResponse(BaseModel):
    conversation_id: str
    response: str
    # Langchain Message 객체 전체를 보내거나, 필요한 정보만 추출해서 보낼 수 있음
    # messages_history: List[Dict[str, str]] 
    # debug_info: Optional[Dict[str, Any]]

# --- API 엔드포인트 ---
@app.post("/chat", response_model=ChatResponse)
async def chat_with_agent(payload: ChatInput = Body(...)):
    logger.info(f"입력 페이로드: {payload}")
    conversation_id = payload.conversation_id if payload.conversation_id else str(uuid.uuid4())
    logger.info(f"대화 ID: {conversation_id}")

    if not mcp_clients_instance:
        logger.error("MCP 클라이언트가 초기화되지 않았습니다. /chat 요청을 처리할 수 없습니다.")
        raise HTTPException(status_code=503, detail="MCP 서비스 연결 불가. 잠시 후 다시 시도해주세요.")

    # 이전 대화 상태 로드 또는 새 상태 초기화
    # LangGraph는 config 객체를 통해 스레드(대화)를 관리합니다.
    config = {"configurable": {"thread_id": conversation_id}}
    
    # 현재 상태를 가져오거나, 첫번째 메시지인 경우 초기 상태 구성
    # (주의: LangGraph의 SqliteSaver는 이전 상태를 자동으로 로드하므로, 명시적 로드는 필요 없을 수 있음
    # 하지만 messages 리스트를 올바르게 구성하기 위해 필요할 수 있음)
    
    # messages 리스트를 구성 (기존 대화가 있다면 가져오고, 아니면 새로 시작)
    # 이 부분은 LangGraph의 체크포인터와 어떻게 상호작용할지에 따라 달라질 수 있습니다.
    # 가장 간단한 방법은 항상 HumanMessage만 전달하고, AgentState의 messages는 그래프 내부에서 관리하는 것입니다.
    current_messages: List[AIMessage] = [HumanMessage(content=payload.message)]

    # AgentState 구성
    # supervisor_node가 current_intent를 설정하므로, 여기서는 messages와 mcp_clients만 전달.
    input_state = AgentState(
        messages=current_messages,
        mcp_clients=mcp_clients_instance,
        # 나머지 필드들은 그래프 실행 중 동적으로 채워짐
        current_intent=None, # supervisor가 입력 메시지를 보고 첫 의도를 결정
        response_to_user=None,
        # ... 기타 필요한 초기값들 (대부분 Optional이므로 None으로 시작 가능)
    )
    logger.debug(f"LangGraph 입력 상태 (초기): {input_state}")

    final_state = None
    agent_response_content = "죄송합니다. 현재 요청을 처리할 수 없습니다."

    try:
        # 비동기 스트림으로 LangGraph 실행
        # astream_events 대신 astream을 사용하여 최종 상태만 받거나, 특정 이벤트만 처리 가능
        async for event_part in langgraph_app.astream(input_state, config=config):
            # astream은 각 노드 실행 후의 전체 상태를 반환할 수 있음
            # 혹은 특정 노드의 출력만 받을 수도 있음 (invoke, batch 등 메서드에 따라 다름)
            # 여기서는 마지막 event_part가 최종 상태라고 가정 (또는 특정 노드 결과 확인)
            # logger.debug(f"스트림 이벤트 부분: {event_part}") # 모든 중간 상태 로깅 (매우 상세)
            
            # event_part가 딕셔너리 형태이고, 키가 노드 이름인 경우가 많음.
            # 어떤 노드의 결과가 최종 응답인지 결정해야 함.
            # 예: supervisor 노드가 최종 응답을 state["response_to_user"]에 담는다고 가정
            if isinstance(event_part, dict):
                # 가장 마지막 supervisor 실행 결과 또는 END로 가기 직전의 상태를 찾을 수 있음
                # 혹은 response_to_user가 채워진 첫번째 상태를 사용할 수도 있음
                # 또는 supervisor_node가 항상 마지막에 호출되어 최종 응답을 결정한다고 가정
                # 아래는 supervisor 노드가 실행될 때마다 그 상태를 final_state로 간주하는 예시
                if "supervisor" in event_part: # supervisor 노드가 최종 응답을 결정한다고 가정
                    final_state = event_part["supervisor"]
                    logger.debug(f"Supervisor 실행 후 상태 업데이트: {final_state.get('response_to_user')}")
                elif any(node_name for node_name in event_part if node_name == END and event_part[node_name]):
                    # END로 끝났을 때, 그 직전 상태가 final_state가 될 수 있음.
                    # 이 경우, event_part는 END 직전 노드의 출력을 포함한 전체 상태일 것.
                    # AgentState 전체를 final_state로 사용하려면, END 이벤트 발생 시의 상태를 저장해야 함.
                    # 하지만 astream의 마지막 요소가 최종 상태일 가능성이 높음.
                    pass

        # astream의 가장 마지막 요소가 최종 상태 업데이트를 포함한다고 가정
        # 또는, config를 사용하여 get_state로 최종 상태를 가져올 수 도 있음.
        current_graph_state = langgraph_app.get_state(config)
        if current_graph_state:
            final_state_values = current_graph_state.values
            logger.info(f"LangGraph 최종 상태 (get_state): {final_state_values}")
            agent_response_content = final_state_values.get("response_to_user", agent_response_content)
            # messages 히스토리도 업데이트 가능
        else:
            logger.warning("그래프 실행 후 최종 상태를 가져오지 못했습니다.")

        if not agent_response_content and final_state and final_state.get("response_to_user"):
             agent_response_content = final_state.get("response_to_user")
        
        logger.info(f"에이전트 최종 응답: {agent_response_content}")

    except Exception as e:
        logger.error(f"LangGraph 실행 중 오류 발생: {e}", exc_info=True)
        # 스택 트레이스 로깅
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"에이전트 처리 중 오류: {str(e)}")

    return ChatResponse(conversation_id=conversation_id, response=agent_response_content)

if __name__ == "__main__":
    import uvicorn
    # .env 파일에서 HOST, PORT 가져오기 (기본값 설정)
    APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT = int(os.getenv("APP_PORT", "8000"))
    logger.info(f"FastAPI 애플리케이션을 {APP_HOST}:{APP_PORT}에서 시작합니다.")
    uvicorn.run(app, host=APP_HOST, port=APP_PORT)
