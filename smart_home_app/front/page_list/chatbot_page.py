import streamlit as st
import requests
import json
import uuid
import asyncio
from schema.state import SessionState, Response
from logging_config import setup_logger

logger = setup_logger(__name__)


# 에이전트 모드 상수 정의
AGENT_MODES = {
    "일반": "🏠",  # 집 아이콘
    "쿠킹": "🍳",  # 요리 아이콘
    "학습": "📚",  # 책 아이콘
    "케어": "🧘"   # 케어 아이콘
}

def generate_session_id():
    """Generate New session id"""
    return str(uuid.uuid4())


def initialize():
    """Initialize session id and message"""
    if SessionState.SESSION_ID.value not in st.session_state:
        st.session_state.session_id = generate_session_id()

    if SessionState.MESSAGES.value not in st.session_state:
        st.session_state.messages = []
        
    # 에이전트 모드 초기화
    if "agent_mode" not in st.session_state:
        st.session_state.agent_mode = "일반"


def get_chat_response(message, session_id=None):
    """Sends a message to the /chat API and returns the response."""
    url = "http://0.0.0.0:8999/chat"
    headers = {"Content-Type": "application/json"}
    data = {Response.MESSAGE.value: message}

    if session_id:
        data[SessionState.SESSION_ID.value] = session_id
    
    # 에이전트 모드 정보도 전달
    data["agent_mode"] = st.session_state.agent_mode

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to server: {e}")
        return None
    except json.JSONDecodeError as e:
        st.error(f"Error decoding JSON response: {e}")
        return None


def render_sidebar():

    with st.sidebar:
        # 에이전트 모드 선택 섹션
        st.header("에이전트 모드")
        
        # 모드 옵션 포맷 함수
        def format_mode(mode):
            return f"{AGENT_MODES[mode]} {mode}"
        
        # 세그먼트 컨트롤로 모드 선택
        selected_mode = st.segmented_control(
            "모드 선택",
            options=list(AGENT_MODES.keys()),
            format_func=format_mode,
            selection_mode="single",
            default=st.session_state.agent_mode
        )
        
        # 모드가 변경되면 세션 상태 업데이트하고 즉시 페이지 리프레시
        if selected_mode and selected_mode != st.session_state.agent_mode:
            st.session_state.agent_mode = selected_mode
            st.success(f"{selected_mode} 모드로 변경되었습니다!")
            # 즉시 페이지 리프레시
            st.rerun()
        
        # 모드별 설명 표시
        mode_descriptions = {
            "일반": "일상적인 도움이 필요할 때 사용하는 표준 모드입니다.",
            "쿠킹": "요리 레시피, 식재료 관리, 주방 가전 제어에 특화된 모드입니다.",
            "학습": "공부, 자료 검색, 학습 일정 관리에 도움을 주는 모드입니다.",
            "케어": "건강 관리, 명상, 수면 케어 등 웰빙에 초점을 맞춘 모드입니다."
        }
        
        st.info(mode_descriptions[st.session_state.agent_mode])
        
        st.divider()

        # 기존 세션 관리 섹션
        st.header("Session Management")

        current_session = (
            st.session_state.session_id
            if st.session_state.session_id
            else "No active session"
        )
        st.info(f"Current Session ID: {current_session}")

        if st.button("New Session"):
            new_session_id = generate_session_id()
            st.session_state.session_id = new_session_id
            st.session_state.messages = []
            st.success(f"New session created with ID: {new_session_id}")
            st.rerun()

        st.divider()


def display_chat_history():
    """Show chat messages stored in session state"""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

async def process_chat(user_input):
    """Process user input asynchronously"""
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        status_placeholder = st.status(
            "Processing your request...", expanded=False
        )
        message_placeholder = st.empty()
        image_container = st.container()

    if not st.session_state.session_id:
        st.session_state.session_id = generate_session_id()
        st.sidebar.info(
            f"New session created with ID: {st.session_state.session_id}"
        )

    response_data = get_chat_response(user_input, st.session_state.session_id)

    if response_data:
        if (
            Response.SESSION_ID.value in response_data
            and response_data[Response.SESSION_ID.value]
            != st.session_state.session_id
        ):
            st.session_state.session_id = response_data[
                Response.SESSION_ID.value
            ]
            st.sidebar.info(
                f"Session ID updated: {st.session_state.session_id}"
            )

        response_text = response_data[Response.RESPONSE.value]
        message_placeholder.markdown(response_text)

        image_data = []
        message_type = "normal"


        status_placeholder.update(
            label="✅ Complete", state="complete", expanded=False
        )

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": response_text,
                "images": image_data,
                "type": message_type,
            }
        )
    else:
        message_placeholder.error(
            "Failed to get a valid response from the server"
        )
        status_placeholder.update(
            label="❌ Error", state="error", expanded=True
        )


def chatbot_page():
    st.title("홈 Assistant")

    initialize()

    render_sidebar()

    # 현재 에이전트 모드 표시
    st.caption(f"{AGENT_MODES[st.session_state.agent_mode]} {st.session_state.agent_mode} 모드로 도움을 드립니다.")

    display_chat_history()

    if prompt := st.chat_input("Enter your message here..."):
        asyncio.run(process_chat(prompt))

