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
CURTAIN_MCP_NAME = os.environ.get("CURTAIN_MCP_NAME", "curtain")
CURTAIN_MCP_HOST = os.environ.get("CURTAIN_MCP_HOST", "0.0.0.0")
CURTAIN_MCP_PORT = int(os.environ.get("CURTAIN_MCP_PORT", 10009))
CURTAIN_MCP_INSTRUCTIONS = os.environ.get("CURTAIN_MCP_INSTRUCTIONS", "커튼 관련 기능을 제어하는 도구입니다. 커튼 열기/닫기, 부분 열기, 스케줄 설정 등의 기능을 제공합니다.")

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("curtain_mcp_server")

# FastMCP 인스턴스 생성
mcp = FastMCP(
    CURTAIN_MCP_NAME,  # MCP 서버 이름
    instructions=CURTAIN_MCP_INSTRUCTIONS,
    host=CURTAIN_MCP_HOST,  # 모든 IP에서 접속 허용
    port=CURTAIN_MCP_PORT,  # 포트 번호
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
async def set_curtain_power(power_state: str) -> Dict[str, Any]:
    """
    커튼을 완전히 열거나 닫습니다.
    
    Args:
        power_state (str): "open" 또는 "close"
        
    Returns:
        Dict[str, Any]: 커튼 제어 결과
    """
    logger.info(f"커튼 전원 제어 요청 수신: {power_state}")
    if power_state not in ["open", "close"]:
        return {"error": "전원 상태는 'open' 또는 'close'여야 합니다."}
    
    result = await mock_api_request("/curtain/power", "POST", {"power_state": power_state})
    return result

@mcp.tool()
async def set_curtain_position(percent: int) -> Dict[str, Any]:
    """
    커튼을 지정한 비율(%)만큼 열거나 닫습니다.
    
    Args:
        percent (int): 커튼을 열 비율 (0~100 사이의 정수, 0: 완전히 닫힘, 100: 완전히 열림)
        
    Returns:
        Dict[str, Any]: 커튼 위치 제어 결과
    """
    logger.info(f"커튼 위치 제어 요청 수신: {percent}%")
    if not (0 <= percent <= 100):
        return {"error": "커튼 위치 값은 0에서 100 사이여야 합니다."}
    
    result = await mock_api_request("/curtain/position", "POST", {"percent": percent})
    return result

@mcp.tool()
async def set_curtain_schedule(time: str, action: str) -> Dict[str, Any]:
    """
    지정한 시간에 커튼을 자동으로 열거나 닫도록 예약합니다.
    
    Args:
        time (str): 예약 시간 (예: "08:00", "18:30")
        action (str): 동작 ("open" 또는 "close")
        
    Returns:
        Dict[str, Any]: 커튼 스케줄 설정 결과
    """
    logger.info(f"커튼 스케줄 설정 요청 수신: {time} {action}")
    if action not in ["open", "close"]:
        return {"error": "동작은 'open' 또는 'close'여야 합니다."}
    
    result = await mock_api_request("/curtain/schedule", "POST", {"time": time, "action": action})
    return result

if __name__ == "__main__":
    # 서버 시작 메시지 출력
    print("커튼 MCP 서버가 실행 중입니다...")
    
    # SSE 트랜스포트를 사용하여 MCP 서버 시작
    mcp.run(transport="sse") 