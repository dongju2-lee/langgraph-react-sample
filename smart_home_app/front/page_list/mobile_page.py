import streamlit as st
import requests
from logging_config import setup_logger

# 로거 설정
logger = setup_logger("mobile_page")

# 모의 서버 URL
MOCK_SERVER_URL = "http://localhost:10000"

# 모바일 서브페이지 상수
MESSAGE_PAGE = "messages"
PERSONALIZATION_PAGE = "personalization"
CALENDAR_PAGE = "calendar"

def get_user_personalization():
    """
    사용자 개인 선호도 정보를 가져옵니다.
    """
    try:
        response = requests.get(f"{MOCK_SERVER_URL}/personalization/preferences", timeout=5)
        if response.status_code == 200:
            # mock-server는 선호도 목록을 리스트로 반환
            return response.json()
        else:
            logger.error(f"개인화 정보 조회 실패: {response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        logger.error(f"개인화 정보 조회 실패: {str(e)}")
        return []

def get_user_calendar():
    """
    모바일 캘린더 정보를 가져옵니다.
    """
    try:
        response = requests.get(f"{MOCK_SERVER_URL}/mobile/calendar", timeout=5)
        if response.status_code == 200:
            # mock-server는 캘린더 일정을 리스트로 반환
            return response.json()
        else:
            logger.error(f"캘린더 정보 조회 실패: {response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        logger.error(f"캘린더 정보 조회 실패: {str(e)}")
        return []

def get_user_messages():
    """
    모바일 메시지 목록을 가져옵니다.
    """
    try:
        response = requests.get(f"{MOCK_SERVER_URL}/mobile/messages", timeout=5)
        if response.status_code == 200:
            # mock-server는 메시지 목록을 리스트로 반환
            return response.json()
        else:
            logger.error(f"메시지 목록 조회 실패: {response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        logger.error(f"메시지 목록 조회 실패: {str(e)}")
        return []

def mobile_page():
    """
    모바일 앱 연동 페이지입니다.
    """
    st.title("📱 모바일 앱 연동")
    st.markdown("---")
    
    # 페이지 설명
    st.markdown("""
    스마트홈 시스템의 모바일 앱과 연동된 정보를 확인하고 관리할 수 있는 페이지입니다.
    사용자 메시지, 개인화 정보, 캘린더 등의 정보를 확인하고 업데이트할 수 있습니다.
    """)
    
    # 서브페이지 네비게이션
    if "mobile_subpage" not in st.session_state:
        st.session_state.mobile_subpage = MESSAGE_PAGE
    
    # 서브페이지 선택 도구
    selected_page = st.selectbox(
        "보기:",
        [MESSAGE_PAGE, PERSONALIZATION_PAGE, CALENDAR_PAGE],
        format_func=lambda x: {
            MESSAGE_PAGE: "📬 메시지",
            PERSONALIZATION_PAGE: "👤 개인화 정보",
            CALENDAR_PAGE: "📅 캘린더"
        }.get(x, x),
        index=[MESSAGE_PAGE, PERSONALIZATION_PAGE, CALENDAR_PAGE].index(st.session_state.mobile_subpage)
    )
    
    # 서브페이지 상태 업데이트
    st.session_state.mobile_subpage = selected_page
    
    # 새로고침 버튼
    if st.button("🔄 새로고침"):
        st.rerun()
    
    st.markdown("---")
    
    # 메시지 페이지
    if selected_page == MESSAGE_PAGE:
        st.header("📬 메시지")
        # 메시지 데이터 가져오기
        with st.spinner("메시지 로딩 중..."):
            messages = get_user_messages()
        if not messages:
            st.info("📭 수신된 메시지가 없습니다.")
        else:
            for msg in messages:
                with st.expander(f"**{msg.get('title', '제목 없음')}** - {msg.get('recipient', '')}"):
                    st.write(msg.get("content", "내용 없음"))
    
    # 개인화 정보 페이지
    elif selected_page == PERSONALIZATION_PAGE:
        st.header("👤 개인화 정보")
        # 개인화 정보 가져오기
        with st.spinner("개인화 정보 로딩 중..."):
            preferences = get_user_personalization()
        if not preferences:
            st.info("저장된 개인화 정보가 없습니다.")
        else:
            st.markdown("### 저장된 선호도")
            for i, pref in enumerate(preferences, 1):
                st.info(f"{i}. {pref.get('description', '')}")
        # 새 개인화 정보 추가 폼
        st.markdown("### 새 개인화 정보 추가")
        with st.form("add_personalization_form"):
            new_info = st.text_area("정보 입력", placeholder="예: 좋아하는 음식은 치킨입니다.")
            submit_button = st.form_submit_button("저장")
            if submit_button and new_info:
                try:
                    response = requests.post(
                        f"{MOCK_SERVER_URL}/personalization/preferences",
                        json={"description": new_info},
                        timeout=5
                    )
                    if response.status_code == 200:
                        st.success("✅ 개인화 정보가 저장되었습니다.")
                        st.rerun()
                    else:
                        st.error(f"❌ 저장 실패: {response.status_code}")
                except requests.exceptions.RequestException as e:
                    st.error(f"❌ 저장 실패: {str(e)}")
    
    # 캘린더 페이지
    elif selected_page == CALENDAR_PAGE:
        st.header("📅 캘린더")
        # 캘린더 정보 가져오기
        with st.spinner("캘린더 정보 로딩 중..."):
            calendar_events = get_user_calendar()
        if not calendar_events:
            st.info("캘린더 정보가 없습니다.")
        else:
            st.markdown("### 일정 목록")
            for event in calendar_events:
                st.info(f"{event.get('date', '')} {event.get('title', '')} - {event.get('content', '')}")
        # 새 일정 추가 폼
        st.markdown("### 새 일정 추가")
        with st.form("add_calendar_form"):
            date = st.text_input("날짜", placeholder="예: 2024-06-01")
            title = st.text_input("제목", placeholder="예: 가족 식사")
            content = st.text_area("일정 내용", placeholder="예: 가족과 저녁식사")
            submit_button = st.form_submit_button("일정 추가")
            if submit_button and date and title and content:
                try:
                    response = requests.post(
                        f"{MOCK_SERVER_URL}/mobile/calendar",
                        json={
                            "date": date,
                            "title": title,
                            "content": content
                        },
                        timeout=5
                    )
                    if response.status_code == 200:
                        st.success("✅ 일정이 추가되었습니다.")
                        st.rerun()
                    else:
                        st.error(f"❌ 저장 실패: {response.status_code}")
                except requests.exceptions.RequestException as e:
                    st.error(f"❌ 저장 실패: {str(e)}")
    
    logger.info(f"모바일 페이지가 로드되었습니다. (서브페이지: {selected_page})") 