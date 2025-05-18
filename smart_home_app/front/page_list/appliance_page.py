import streamlit as st
import requests
import time
from logging_config import setup_logger

# 로거 설정
logger = setup_logger("appliance_page")

# 모의 서버 URL
MOCK_SERVER_URL = "http://localhost:10000"

def get_refrigerator_display():
    """냉장고 디스플레이 정보 가져오기"""
    try:
        response = requests.get(f"{MOCK_SERVER_URL}/refrigerator/cooking-state", timeout=2)
        if response.status_code == 200:
            data = response.json()
            # 예시: {"cooking_state": "요리중"} 또는 {"cooking_state": "대기중"}
            state = data.get("cooking_state", "미진행")
            if state == "요리중":
                return f"🟢 요리 상태: 요리중"
            elif state == "대기중":
                return f"🟡 요리 상태: 대기중"
            else:
                return f"⚪️ 요리 상태: {state}"
        else:
            return f"🔴 오류 발생: 서버 응답 코드 {response.status_code}"
    except Exception as e:
        logger.error(f"냉장고 상태 확인 오류: {str(e)}")
        return f"🔴 연결 오류: {str(e)}"

def get_refrigerator_food_items():
    """냉장고 식재료 목록 가져오기"""
    try:
        response = requests.get(f"{MOCK_SERVER_URL}/refrigerator/food-items", timeout=2)
        if response.status_code == 200:
            data = response.json()
            # 예시: {"items": [{"name": "소고기", "quantity": "200g"}, ...]}
            return data.get("items", [])
        else:
            logger.error(f"냉장고 식재료 목록 조회 오류: 서버 응답 코드 {response.status_code}")
            return []
    except Exception as e:
        logger.error(f"냉장고 식재료 목록 조회 오류: {str(e)}")
        return []

def get_induction_state():
    """인덕션 상태 가져오기 (mock-server의 /api/induction/status 사용)"""
    try:
        response = requests.get(f"{MOCK_SERVER_URL}/api/induction/status", timeout=2)
        if response.status_code == 200:
            data = response.json()
            power_state = data.get("power", False)
            cooking = data.get("cooking", False)
            heat_level = data.get("heat_level", None)
            message = data.get("message", "")
            
            # 화력 단계에 따른 한글 표시
            heat_level_korean = {
                "HIGH": "강불",
                "MEDIUM": "중불",
                "LOW": "약불"
            }.get(heat_level, "")
            
            if power_state:
                st.success("전원이 켜져 있습니다")
                st.progress(100)
                if cooking:
                    return f"🟢 전원 켜짐 (조리중 - {heat_level_korean}) - {message}"
                else:
                    return f"🟢 전원 켜짐 (대기) - {message}"
            else:
                st.error("전원이 꺼져 있습니다")
                st.progress(0)
                return f"🔴 전원 꺼짐 - {message}"
        else:
            return f"🔴 오류 발생: 서버 응답 코드 {response.status_code}"
    except Exception as e:
        logger.error(f"인덕션 상태 확인 오류: {str(e)}")
        return f"🔴 연결 오류: {str(e)}"

def get_microwave_state():
    """전자레인지 상태 가져오기 (mock-server의 /api/microwave/status 사용)"""
    try:
        response = requests.get(f"{MOCK_SERVER_URL}/api/microwave/status", timeout=2)
        if response.status_code == 200:
            data = response.json()
            # 예시: {"power": true, "cooking": false, "message": "..."}
            power_state = data.get("power", False)
            cooking = data.get("cooking", False)
            message = data.get("message", "")
            if power_state:
                st.success(f"전원이 켜져 있습니다")
                st.progress(100)
                if cooking:
                    return f"🟢 전원 켜짐 (조리중) - {message}"
                else:
                    return f"🟢 전원 켜짐 (대기) - {message}"
            else:
                st.error("전원이 꺼져 있습니다")
                st.progress(0)
                return f"🔴 전원 꺼짐 - {message}"
        else:
            return f"🔴 오류 발생: 서버 응답 코드 {response.status_code}"
    except Exception as e:
        logger.error(f"전자레인지 상태 확인 오류: {str(e)}")
        return f"🔴 연결 오류: {str(e)}"

def get_tv_state():
    """TV 상태 가져오기"""
    try:
        response = requests.get(f"{MOCK_SERVER_URL}/tv/status", timeout=2)
        if response.status_code == 200:
            data = response.json()
            power_state = data.get("power", False)
            current_channel = data.get("current_channel", "")
            volume = data.get("volume", 0)
            message = data.get("message", "")
            
            # 채널 목록도 얻기
            channels_response = requests.get(f"{MOCK_SERVER_URL}/tv/channels", timeout=2)
            channels_count = 0
            if channels_response.status_code == 200:
                channels_data = channels_response.json()
                channels_count = len(channels_data.get("channels", []))
            
            if power_state:
                st.success("TV가 켜져 있습니다")
                st.progress(100)
                return f"🟢 TV 켜짐 - 채널: {current_channel}, 볼륨: {volume} - {channels_count}개 채널 이용 가능"
            else:
                st.error("TV가 꺼져 있습니다")
                st.progress(0)
                return f"🔴 TV 꺼짐 - {message}"
        else:
            return f"🔴 오류 발생: 서버 응답 코드 {response.status_code}"
    except Exception as e:
        logger.error(f"TV 상태 확인 오류: {str(e)}")
        return f"🔴 연결 오류: {str(e)}"

def get_light_state():
    """조명 상태 가져오기"""
    try:
        response = requests.get(f"{MOCK_SERVER_URL}/light/status", timeout=2)
        if response.status_code == 200:
            data = response.json()
            power_state = data.get("power", False)
            brightness = data.get("brightness", 0)
            color = data.get("color", "")
            mode = data.get("mode", "")
            message = data.get("message", "")
            
            if power_state:
                st.success("조명이 켜져 있습니다")
                st.progress(brightness)
                return f"🟢 조명 켜짐 - 밝기: {brightness}%, 색상: {color}, 모드: {mode}"
            else:
                st.error("조명이 꺼져 있습니다")
                st.progress(0)
                return f"🔴 조명 꺼짐 - {message}"
        else:
            return f"🔴 오류 발생: 서버 응답 코드 {response.status_code}"
    except Exception as e:
        logger.error(f"조명 상태 확인 오류: {str(e)}")
        return f"🔴 연결 오류: {str(e)}"

def get_curtain_state():
    """커튼 상태 가져오기"""
    try:
        response = requests.get(f"{MOCK_SERVER_URL}/curtain/status", timeout=2)
        if response.status_code == 200:
            data = response.json()
            power_state = data.get("power_state", "close")
            position = data.get("position", 0)
            is_open = data.get("is_open", False)
            message = data.get("message", "")
            
            if is_open:
                st.success(f"커튼이 {position}% 열려 있습니다")
                st.progress(position)
                return f"🟢 {message}"
            else:
                st.error("커튼이 닫혀 있습니다")
                st.progress(0)
                return f"🔴 {message}"
        else:
            return f"🔴 오류 발생: 서버 응답 코드 {response.status_code}"
    except Exception as e:
        logger.error(f"커튼 상태 확인 오류: {str(e)}")
        return f"🔴 연결 오류: {str(e)}"

def get_audio_state():
    """오디오 상태 가져오기"""
    try:
        response = requests.get(f"{MOCK_SERVER_URL}/audio/status", timeout=2)
        if response.status_code == 200:
            data = response.json()
            playing = data.get("playing", False)
            current_playlist = data.get("current_playlist", None)
            current_song = data.get("current_song", None)
            volume = data.get("volume", 0)
            message = data.get("message", "")
            power_state = data.get("power", "off")
            
            # 전원 켜기/끄기 버튼 생성 (오디오 상태와 반대 동작 버튼 표시)
            power_button_label = "🔌 전원 켜기" if power_state == "off" else "🔌 전원 끄기"
            target_state = "on" if power_state == "off" else "off"
            
            if st.button(power_button_label):
                try:
                    power_response = requests.post(
                        f"{MOCK_SERVER_URL}/audio/power", 
                        json={"power_state": target_state}, 
                        timeout=2
                    )
                    if power_response.status_code == 200:
                        st.success(f"오디오 전원이 {target_state}으로 변경되었습니다.")
                        st.rerun()  # 페이지 새로고침
                    else:
                        st.error(f"오디오 전원 변경 실패: {power_response.status_code}")
                except Exception as e:
                    st.error(f"오디오 전원 변경 오류: {str(e)}")
            
            # 전원이 꺼진 경우
            if power_state == "off":
                st.error("오디오가 꺼져 있습니다")
                st.progress(0)
                return f"🔴 오디오 전원 꺼짐: {message}"
            # 전원이 켜져 있는 경우
            elif playing:
                st.success(f"오디오 재생 중: {current_song or '알 수 없는 곡'}")
                st.progress(volume * 10)  # 0-10 볼륨을 0-100%로 변환
                return f"🟢 {message}"
            elif current_playlist:
                st.warning(f"플레이리스트 선택됨: {current_playlist}")
                st.progress(50)
                return f"🟡 {message}"
            else:
                st.info("오디오가 켜져 있지만 재생 중이 아닙니다")
                st.progress(0)
                return f"🟡 {message}"
        else:
            return f"🔴 오류 발생: 서버 응답 코드 {response.status_code}"
    except Exception as e:
        logger.error(f"오디오 상태 확인 오류: {str(e)}")
        return f"🔴 연결 오류: {str(e)}"

def appliance_page():
    """가전제품 상태 페이지 표시"""
    st.title("🔌 가전제품 모니터링")
    st.markdown("---")
    
    # 수동 새로고침 버튼을 사이드바로 이동
    with st.sidebar:
        st.subheader("수동 새로고침")
        if st.button("🔄 새로고침"):
            st.rerun()
    
    # 첫 번째 줄: 냉장고, 인덕션, 전자레인지
    st.subheader("주방 가전")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("냉장고")
        refrigerator_state = get_refrigerator_display()
        st.markdown(f"### {refrigerator_state}")
        
        # 식재료 목록 expander 추가
        with st.expander("🍎 냉장고 식재료 목록"):
            food_items = get_refrigerator_food_items()
            if food_items:
                for item in food_items:
                    st.markdown(f"- **{item['name']}**: {item['quantity']}")
            else:
                st.markdown("식재료 정보를 불러올 수 없습니다.")
    
    with col2:
        st.subheader("인덕션")
        induction_state = get_induction_state()
        st.markdown(f"### {induction_state}")
    
    with col3:
        st.subheader("전자레인지")
        microwave_state = get_microwave_state()
        st.markdown(f"### {microwave_state}")
    
    # 두 번째 줄: TV, 조명, 커튼
    st.markdown("---")
    st.subheader("거실 가전")
    col4, col5, col6 = st.columns(3)
    
    with col4:
        st.subheader("TV")
        tv_state = get_tv_state()
        st.markdown(f"### {tv_state}")
        
        # TV 채널 목록 expander 추가
        with st.expander("📺 TV 채널 목록"):
            try:
                response = requests.get(f"{MOCK_SERVER_URL}/tv/channels", timeout=2)
                if response.status_code == 200:
                    data = response.json()
                    channels = data.get("channels", [])
                    if channels:
                        for channel in channels:
                            st.markdown(f"- **{channel.get('name')}**: {channel.get('description')}")
                    else:
                        st.markdown("채널 정보를 불러올 수 없습니다.")
                else:
                    st.markdown("채널 정보를 불러올 수 없습니다.")
            except Exception as e:
                st.markdown(f"채널 정보를 불러올 수 없습니다: {str(e)}")
    
    with col5:
        st.subheader("조명")
        light_state = get_light_state()
        st.markdown(f"### {light_state}")
    
    with col6:
        st.subheader("커튼")
        curtain_state = get_curtain_state()
        st.markdown(f"### {curtain_state}")
    
    # 세 번째 줄: 오디오
    st.markdown("---")
    st.subheader("엔터테인먼트 가전")
    col7, col8, col9 = st.columns(3)
    
    with col7:
        st.subheader("오디오")
        audio_state = get_audio_state()
        st.markdown(f"### {audio_state}")
        
        # 오디오 플레이리스트 expander 추가
        with st.expander("🎵 오디오 플레이리스트"):
            try:
                response = requests.get(f"{MOCK_SERVER_URL}/audio/playlists", timeout=2)
                if response.status_code == 200:
                    data = response.json()
                    playlists = data.get("playlists", [])
                    if playlists:
                        for playlist in playlists:
                            st.markdown(f"- **{playlist.get('name')}**: {playlist.get('description')}")
                    else:
                        st.markdown("플레이리스트 정보를 불러올 수 없습니다.")
                else:
                    st.markdown("플레이리스트 정보를 불러올 수 없습니다.")
            except Exception as e:
                st.markdown(f"플레이리스트 정보를 불러올 수 없습니다: {str(e)}")
    
    # 나머지 열은 비워두거나 추후 다른 가전제품 추가 가능
    with col8:
        pass
    
    with col9:
        pass
    
    logger.info("가전제품 페이지가 로드되었습니다.") 