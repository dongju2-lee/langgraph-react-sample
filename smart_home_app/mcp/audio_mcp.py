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
AUDIO_MCP_INSTRUCTIONS = os.environ.get("AUDIO_MCP_INSTRUCTIONS", "오디오 관련 기능을 제어하는 도구입니다. 음악 재생, 정지, 볼륨 조절, 플레이리스트 조회 등의 기능을 제공합니다.")

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
async def play_audio(playlist: Optional[str] = None, song: Optional[str] = None) -> Dict[str, Any]:
    """
    음악/플레이리스트/특정 곡을 재생합니다.
    
    Args:
        playlist (Optional[str]): 재생할 플레이리스트 이름 (예: "명상", "공부")
        song (Optional[str]): 재생할 곡 이름 (예: "잔잔음악", "백색소음")
        
    Returns:
        Dict[str, Any]: 재생 결과
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
    
    Returns:
        Dict[str, Any]: 정지 결과
    """
    logger.info("오디오 정지 요청 수신")
    result = await mock_api_request("/audio/stop", "POST", {})
    return result

@mcp.tool()
async def set_audio_volume(level: int) -> Dict[str, Any]:
    """
    오디오 볼륨을 조절합니다.
    
    Args:
        level (int): 볼륨 값 (0~10 사이의 정수)
        
    Returns:
        Dict[str, Any]: 볼륨 조절 결과
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
    
    Args:
        playlist (str): 플레이리스트 이름 (예: "명상", "신나는 음악", "공부")
        
    Returns:
        Dict[str, Any]: 플레이리스트 선택 결과
    """
    logger.info(f"오디오 플레이리스트 선택 요청 수신: {playlist}")
    result = await mock_api_request("/audio/playlist", "POST", {"playlist": playlist})
    return result

@mcp.tool()
async def get_audio_playlists() -> Dict[str, Any]:
    """
    이용 가능한 모든 플레이리스트 목록을 조회합니다.
    
    Returns:
        Dict[str, Any]: 플레이리스트 목록
    """
    logger.info("플레이리스트 목록 조회 요청 수신")
    result = await mock_api_request("/audio/playlists", "GET")
    return result

@mcp.tool()
async def get_playlist_songs(playlist_name: str) -> Dict[str, Any]:
    """
    특정 플레이리스트에 포함된 모든 곡 목록을 조회합니다.
    
    Args:
        playlist_name (str): 조회할 플레이리스트 이름 (예: "명상", "신나는 음악", "공부")
        
    Returns:
        Dict[str, Any]: 플레이리스트 내 곡 목록
    """
    logger.info(f"플레이리스트 '{playlist_name}' 곡 목록 조회 요청 수신")
    result = await mock_api_request(f"/audio/playlists/{playlist_name}/songs", "GET")
    return result

if __name__ == "__main__":
    # 서버 시작 메시지 출력
    print("오디오 MCP 서버가 실행 중입니다...")
    
    # SSE 트랜스포트를 사용하여 MCP 서버 시작
    mcp.run(transport="sse") 