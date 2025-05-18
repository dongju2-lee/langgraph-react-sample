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
LIGHT_MCP_NAME = os.environ.get("LIGHT_MCP_NAME", "light")
LIGHT_MCP_HOST = os.environ.get("LIGHT_MCP_HOST", "0.0.0.0")
LIGHT_MCP_PORT = int(os.environ.get("LIGHT_MCP_PORT", 10008))
LIGHT_MCP_INSTRUCTIONS = os.environ.get("LIGHT_MCP_INSTRUCTIONS", "조명 관련 기능을 제어하는 도구입니다. 조명 전원 제어, 밝기 조절, 색상 변경, 모드 설정 등의 기능을 제공합니다.")

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("light_mcp_server")

# FastMCP 인스턴스 생성
mcp = FastMCP(
    LIGHT_MCP_NAME,  # MCP 서버 이름
    instructions=LIGHT_MCP_INSTRUCTIONS,
    host=LIGHT_MCP_HOST,  # 모든 IP에서 접속 허용
    port=LIGHT_MCP_PORT,  # 포트 번호
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
async def set_light_power(power_state: str) -> Dict[str, Any]:
    """
    조명 전원을 켜거나 끕니다.
    
    Args:
        power_state (str): "on" 또는 "off"
        
    Returns:
        Dict[str, Any]: 조명 전원 제어 결과
    """
    logger.info(f"조명 전원 제어 요청 수신: {power_state}")
    if power_state not in ["on", "off"]:
        return {"error": "전원 상태는 'on' 또는 'off'여야 합니다."}
    
    result = await mock_api_request("/light/power", "POST", {"power_state": power_state})
    return result

@mcp.tool()
async def set_light_brightness(level: int) -> Dict[str, Any]:
    """
    조명 밝기를 조절합니다.
    
    Args:
        level (int): 밝기 값 (0~100 사이의 정수)
        
    Returns:
        Dict[str, Any]: 밝기 조절 결과
    """
    logger.info(f"조명 밝기 조절 요청 수신: {level}")
    if not (0 <= level <= 100):
        return {"error": "밝기 값은 0에서 100 사이여야 합니다."}
    
    result = await mock_api_request("/light/brightness", "POST", {"level": level})
    return result

@mcp.tool()
async def set_light_color(color: str) -> Dict[str, Any]:
    """
    조명 색상을 변경합니다.
    
    Args:
        color (str): 색상명 (예: "warm", "cool", "blue")
        
    Returns:
        Dict[str, Any]: 색상 변경 결과
    """
    logger.info(f"조명 색상 변경 요청 수신: {color}")
    result = await mock_api_request("/light/color", "POST", {"color": color})
    return result

@mcp.tool()
async def set_light_mode(mode: str) -> Dict[str, Any]:
    """
    조명 프리셋 모드를 적용합니다.
    
    Args:
        mode (str): 프리셋 모드명 (예: "study", "relax", "healing")
        
    Returns:
        Dict[str, Any]: 모드 적용 결과
    """
    logger.info(f"조명 모드 적용 요청 수신: {mode}")
    result = await mock_api_request("/light/mode", "POST", {"mode": mode})
    return result

if __name__ == "__main__":
    # 서버 시작 메시지 출력
    print("조명 MCP 서버가 실행 중입니다...")
    
    # SSE 트랜스포트를 사용하여 MCP 서버 시작
    mcp.run(transport="sse") 