from mcp.server.fastmcp import FastMCP
import os
import requests
import json
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()
MOCK_SERVER_URL = os.environ.get("MOCK_SERVER_URL", "http://localhost:10000")
TV_MCP_NAME = os.environ.get("TV_MCP_NAME", "tv")
TV_MCP_HOST = os.environ.get("TV_MCP_HOST", "0.0.0.0")
TV_MCP_PORT = int(os.environ.get("TV_MCP_PORT", 10006))
TV_MCP_INSTRUCTIONS = os.environ.get("TV_MCP_INSTRUCTIONS", "TV 관련 기능을 제어하는 도구입니다. TV 전원 제어, 채널 변경, 볼륨 조절, 채널 목록 조회 등의 기능을 제공합니다.")

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("tv_mcp_server")

# FastMCP 인스턴스 생성
mcp = FastMCP(
    TV_MCP_NAME,  # MCP 서버 이름
    instructions=TV_MCP_INSTRUCTIONS,
    host=TV_MCP_HOST,  # 모든 IP에서 접속 허용
    port=TV_MCP_PORT,  # 포트 번호
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
async def set_tv_power(power_state: str) -> Dict[str, Any]:
    """
    TV 전원을 켜거나 끕니다.
    
    Args:
        power_state (str): "on" 또는 "off"
        
    Returns:
        Dict[str, Any]: TV 전원 제어 결과
    """
    logger.info(f"TV 전원 제어 요청 수신: {power_state}")
    if power_state not in ["on", "off"]:
        return {"error": "전원 상태는 'on' 또는 'off'여야 합니다."}
    
    result = await mock_api_request("/tv/power", "POST", {"power_state": power_state})
    return result

@mcp.tool()
async def change_tv_channel(channel: str) -> Dict[str, Any]:
    """
    TV 채널을 변경합니다.
    
    Args:
        channel (str): 변경할 채널명 (예: "EBC", "MBB", "너튜브" 등)
        
    Returns:
        Dict[str, Any]: 채널 변경 결과
    """
    logger.info(f"TV 채널 변경 요청 수신: {channel}")
    result = await mock_api_request("/tv/channel", "POST", {"channel": channel})
    return result

@mcp.tool()
async def set_tv_volume(level: int) -> Dict[str, Any]:
    """
    TV 볼륨을 조절합니다.
    
    Args:
        level (int): 볼륨 값 (0~100 사이의 정수)
        
    Returns:
        Dict[str, Any]: 볼륨 조절 결과
    """
    logger.info(f"TV 볼륨 조절 요청 수신: {level}")
    if not (0 <= level <= 100):
        return {"error": "볼륨 값은 0에서 100 사이여야 합니다."}
    
    result = await mock_api_request("/tv/volume", "POST", {"level": level})
    return result

@mcp.tool()
async def get_tv_channels() -> Dict[str, Any]:
    """
    TV 채널 목록을 조회합니다.
    
    Returns:
        Dict[str, Any]: TV 채널 목록
    """
    logger.info("TV 채널 목록 조회 요청 수신")
    result = await mock_api_request("/tv/channels", "GET")
    return result

if __name__ == "__main__":
    # 서버 시작 메시지 출력
    print("TV MCP 서버가 실행 중입니다...")
    
    # SSE 트랜스포트를 사용하여 MCP 서버 시작
    mcp.run(transport="sse") 