from mcp.server.fastmcp import FastMCP
import os
import requests
import json
import logging
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()
MOCK_SERVER_URL = os.environ.get("MOCK_SERVER_URL", "http://localhost:10000")
AUDIO_MCP_NAME = os.environ.get("AUDIO_MCP_NAME", "audio")
AUDIO_MCP_HOST = os.environ.get("AUDIO_MCP_HOST", "0.0.0.0")
AUDIO_MCP_PORT = int(os.environ.get("AUDIO_MCP_PORT", 10007))
AUDIO_MCP_INSTRUCTIONS = os.environ.get("AUDIO_MCP_INSTRUCTIONS", "오디오 관련 기능을 제어하는 도구입니다. 음악 재생, 정지, 볼륨 조절, 플레이리스트 조회, 전원 켜기/끄기 등의 기능을 제공합니다.")

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("audio_mcp_server")

# FastMCP 인스턴스 생성
mcp = FastMCP(
    AUDIO_MCP_NAME,  # MCP 서버 이름
    instructions=AUDIO_MCP_INSTRUCTIONS,
    host=AUDIO_MCP_HOST,  # 모든 IP에서 접속 허용
    port=AUDIO_MCP_PORT,  # 포트 번호
)

# 모의 API 요청 함수
async def mock_api_request(path: str, method: str = "GET", data: Optional[Dict] = None) -> Dict:
    """실제 모의 서버에 API 요청을 보내는 함수"""
    url = f"{MOCK_SERVER_URL}{path}"
    logger.info(f"모의 서버 API 요청: {method} {url}")
    
    try:
        if method.upper() == "GET":
            response = requests.get(url)
        elif method.upper() == "POST":
            response = requests.post(url, json=data)
        else:
            return {"error": f"지원하지 않는 HTTP 메서드: {method}"}
        
        response.raise_for_status()
        result = response.json()
        logger.info(f"모의 서버 응답: {json.dumps(result, ensure_ascii=False)}")
        return result
    except Exception as e:
        logger.error(f"모의 서버 요청 실패: {str(e)}")
        return {"error": f"모의 서버 요청 실패: {str(e)}"}

@mcp.tool()
async def set_audio_power(power_state: str) -> Dict[str, Any]:
    """
    오디오 시스템의 전원을 켜거나 끕니다.
    
    이 도구는 오디오 시스템의 전원 상태를 제어합니다. 전원을 켜면 오디오가 준비 상태가 되며,
    전원을 끄면 현재 재생 중인 음악이 있으면 자동으로 중지됩니다.
    
    Args:
        power_state (str): "on" 또는 "off" 값만 허용됩니다.
            - "on": 오디오 시스템 전원을 켭니다.
            - "off": 오디오 시스템 전원을 끄고 재생 중인 음악이 있으면 중지합니다.
        
    Returns:
        Dict[str, Any]: 전원 제어 결과를 포함하는 딕셔너리 형태의 응답
            - result: 작업 결과 상태 ("success", "error" 등)
            - message: 결과 설명 메시지
    
    예시:
        set_audio_power("on") -> 오디오 전원을 켭니다.
        set_audio_power("off") -> 오디오 전원을 끕니다.
    """
    logger.info(f"오디오 전원 제어 요청 수신: {power_state}")
    if power_state not in ["on", "off"]:
        return {"error": "전원 상태는 'on' 또는 'off'여야 합니다."}
    
    result = await mock_api_request("/audio/power", "POST", {"power_state": power_state})
    return result

@mcp.tool()
async def play_audio(playlist: Optional[str] = None, song: Optional[str] = None) -> Dict[str, Any]:
    """
    음악/플레이리스트/특정 곡을 재생합니다.
    
    이 도구는 지정된 플레이리스트나 특정 곡을 재생합니다. 오디오 시스템이 꺼져 있는 경우
    자동으로 전원을 켠 후 재생을 시작합니다.
    
    Args:
        playlist (Optional[str]): 재생할 플레이리스트 이름 (예: "명상", "공부")
        song (Optional[str]): 재생할 곡 이름 (예: "잔잔음악", "백색소음")
        
    Returns:
        Dict[str, Any]: 재생 결과를 포함하는 딕셔너리 형태의 응답
    
    참고:
        playlist와 song 중 하나는 반드시 지정해야 합니다.
        둘 다 지정된 경우에는 song이 우선적으로 재생됩니다.
        오디오 시스템이 꺼져 있는 경우 자동으로 전원이 켜집니다.
    """
    logger.info(f"오디오 재생 요청 수신: 플레이리스트={playlist}, 곡={song}")
    
    # playlist와 song 중 하나는 있어야 함
    if playlist is None and song is None:
        return {"error": "플레이리스트나 곡 이름 중 하나는 지정해야 합니다."}
    
    data = {}
    if playlist:
        data["playlist"] = playlist
    if song:
        data["song"] = song
        
    result = await mock_api_request("/audio/play", "POST", data)
    return result

@mcp.tool()
async def stop_audio() -> Dict[str, Any]:
    """
    현재 재생 중인 모든 음악을 정지합니다.
    
    이 도구는 현재 재생 중인 오디오를 즉시 중지합니다. 오디오 시스템의 전원은 
    그대로 유지되며, 선택된 플레이리스트 정보도 보존됩니다.
    
    Returns:
        Dict[str, Any]: 정지 결과를 포함하는 딕셔너리 형태의 응답
    
    참고:
        오디오 시스템이 꺼져 있거나 이미 재생 중이 아닌 경우에는 오류가 반환될 수 있습니다.
    """
    logger.info("오디오 정지 요청 수신")
    result = await mock_api_request("/audio/stop", "POST", {})
    return result

@mcp.tool()
async def set_audio_volume(level: int) -> Dict[str, Any]:
    """
    오디오 볼륨을 조절합니다.
    
    이 도구는 오디오 시스템의 볼륨 레벨을 조정합니다. 볼륨 값은 0부터 10까지의 정수로 설정할 수 있으며,
    0은 음소거, 10은 최대 볼륨을 의미합니다.
    
    Args:
        level (int): 볼륨 값 (0~10 사이의 정수)
        
    Returns:
        Dict[str, Any]: 볼륨 조절 결과를 포함하는 딕셔너리 형태의 응답
    
    참고:
        오디오 시스템이 꺼져 있는 경우에는 볼륨을 조절할 수 없으며 오류가 반환됩니다.
    """
    logger.info(f"오디오 볼륨 조절 요청 수신: {level}")
    if not (0 <= level <= 10):
        return {"error": "볼륨 값은 0에서 10 사이여야 합니다."}
    
    result = await mock_api_request("/audio/volume", "POST", {"level": level})
    return result

@mcp.tool()
async def set_audio_playlist(playlist: str) -> Dict[str, Any]:
    """
    플레이리스트를 선택합니다 (자동 재생되지 않음).
    
    이 도구는 지정된 플레이리스트를 현재 선택된 플레이리스트로 설정합니다.
    플레이리스트를 선택해도 자동으로 재생되지는 않습니다. 재생을 시작하려면 
    별도로 play_audio 기능을 사용해야 합니다.
    
    Args:
        playlist (str): 플레이리스트 이름 (예: "명상", "신나는 음악", "공부")
        
    Returns:
        Dict[str, Any]: 플레이리스트 선택 결과를 포함하는 딕셔너리 형태의 응답
    
    참고:
        오디오 시스템이 꺼져 있는 경우 자동으로 전원이 켜지게 됩니다.
        존재하지 않는 플레이리스트를 지정하면 오류가 반환됩니다.
    """
    logger.info(f"오디오 플레이리스트 선택 요청 수신: {playlist}")
    result = await mock_api_request("/audio/playlist", "POST", {"playlist": playlist})
    return result

@mcp.tool()
async def get_audio_playlists() -> Dict[str, Any]:
    """
    이용 가능한 모든 플레이리스트 목록을 조회합니다.
    
    이 도구는 시스템에서 사용 가능한 모든 오디오 플레이리스트의 목록을 반환합니다.
    각 플레이리스트에는 이름, 설명, 카테고리 등의 정보가 포함됩니다.
    
    Returns:
        Dict[str, Any]: 플레이리스트 목록을 포함하는 딕셔너리 형태의 응답
    
    응답 예시:
        {
            "playlists": [
                {"name": "명상", "description": "마음의 안정을 찾는 데 도움이 되는 잔잔한 음악 모음", "category": "힐링"},
                {"name": "신나는 음악", "description": "기분을 업시키고 활력을 불어넣는 신나는 음악 모음", "category": "댄스/팝"},
                {"name": "공부", "description": "집중력을 높이고 학습 효율을 높여주는 음악 모음", "category": "집중"}
            ]
        }
    """
    logger.info("플레이리스트 목록 조회 요청 수신")
    result = await mock_api_request("/audio/playlists", "GET")
    return result

@mcp.tool()
async def get_playlist_songs(playlist_name: str) -> Dict[str, Any]:
    """
    특정 플레이리스트에 포함된 모든 곡 목록을 조회합니다.
    
    이 도구는 지정된 플레이리스트에 포함된 모든 곡의 목록을 반환합니다.
    각 곡에는, 제목과 재생 시간 등의 정보가 포함됩니다.
    
    Args:
        playlist_name (str): 조회할 플레이리스트 이름 (예: "명상", "신나는 음악", "공부")
        
    Returns:
        Dict[str, Any]: 플레이리스트 내 곡 목록을 포함하는 딕셔너리 형태의 응답
    
    응답 예시:
        {
            "playlist_name": "명상",
            "songs": [
                {"title": "잔잔음악", "duration": "5:30"},
                {"title": "바다 파도 소리", "duration": "10:00"},
                {"title": "새소리와 함께하는 명상", "duration": "8:45"}
            ]
        }
    """
    logger.info(f"플레이리스트 '{playlist_name}' 곡 목록 조회 요청 수신")
    result = await mock_api_request(f"/audio/playlists/{playlist_name}/songs", "GET")
    return result

@mcp.tool()
async def get_audio_status() -> Dict[str, Any]:
    """
    오디오 시스템의 현재 상태를 조회합니다.
    
    이 도구는 오디오 시스템의 현재 전원 상태, 재생 상태, 볼륨, 현재 선택된 플레이리스트,
    재생 중인 곡 등 전반적인 상태 정보를 반환합니다.
    
    Returns:
        Dict[str, Any]: 오디오 상태 정보를 포함하는 딕셔너리 형태의 응답
        
    응답에 포함되는 정보:
        - power: 전원 상태 ("on" 또는 "off")
        - playing: 재생 중 여부 (true/false)
        - volume: 현재 볼륨 (0-10)
        - current_playlist: 현재 선택된 플레이리스트 이름
        - current_song: 현재 재생 중인 곡 이름
        - message: 오디오 상태를 설명하는 메시지
    """
    logger.info("오디오 상태 조회 요청 수신")
    result = await mock_api_request("/audio/status", "GET")
    return result

if __name__ == "__main__":
    # 서버 시작 메시지 출력
    print("오디오 MCP 서버가 실행 중입니다...")
    
    # SSE 트랜스포트를 사용하여 MCP 서버 시작
    mcp.run(transport="sse") 