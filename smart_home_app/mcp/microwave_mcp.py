import json
import requests
from typing import Dict, Any, Optional
from mcp.server.fastmcp import FastMCP
import os
import logging
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()
MOCK_SERVER_URL = os.environ.get("MOCK_SERVER_URL", "http://localhost:10000")
MICROWAVE_MCP_NAME = os.environ.get("MICROWAVE_MCP_NAME", "microwave")
MICROWAVE_MCP_HOST = os.environ.get("MICROWAVE_MCP_HOST", "0.0.0.0")
MICROWAVE_MCP_PORT = int(os.environ.get("MICROWAVE_MCP_PORT", 10003))
MICROWAVE_MCP_INSTRUCTIONS = os.environ.get("MICROWAVE_MCP_INSTRUCTIONS", "전자레인지를 제어하는 도구입니다. 전원 상태 확인, 전원 상태 변경, 조리 시작, 남은 시간 확인 등의 기능을 제공합니다.")

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("microwave_mcp_server")

# FastMCP 인스턴스 생성
mcp = FastMCP(
    MICROWAVE_MCP_NAME,  # MCP 서버 이름
    instructions=MICROWAVE_MCP_INSTRUCTIONS,
    host=MICROWAVE_MCP_HOST,  # 모든 IP에서 접속 허용
    port=MICROWAVE_MCP_PORT,  # 포트 번호
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
async def get_microwave_status() -> Dict[str, Any]:
    """
    전자레인지 상태를 조회합니다.
    전원 상태(켜짐/꺼짐), 조리 여부, 남은 시간 등의 정보를 반환합니다.
    
    Returns:
        Dict[str, Any]: 전자레인지 상태 정보
    """
    logger.info("전자레인지 상태 조회 요청 수신")
    result = await mock_api_request("/api/microwave/status")
    return result

@mcp.tool()
async def toggle_microwave_power() -> Dict[str, Any]:
    """
    전자레인지 전원을 켜거나 끕니다.
    현재 전원 상태를 반대로 변경합니다. (켜져 있으면 끄고, 꺼져 있으면 켭니다)
    
    Returns:
        Dict[str, Any]: 작업 결과
    """
    logger.info("전자레인지 전원 토글 요청 수신")
    result = await mock_api_request("/api/microwave/power", "POST")
    return result

@mcp.tool()
async def start_microwave_cooking(seconds: int) -> Dict[str, Any]:
    """
    전자레인지 조리를 시작합니다.
    
    Args:
        seconds (int): 조리 시간(초)
        
    Returns:
        Dict[str, Any]: 작업 결과
    """
    logger.info(f"전자레인지 조리 시작 요청 수신: {seconds}초")
    
    if seconds <= 0:
        logger.error("조리 시간은 0보다 커야 합니다.")
        return {"error": "조리 시간은 0보다 커야 합니다."}
    
    result = await mock_api_request("/api/microwave/start", "POST", {"seconds": seconds})
    return result

@mcp.tool()
async def stop_microwave_cooking() -> Dict[str, Any]:
    """
    전자레인지 조리를 중단합니다.
    
    Returns:
        Dict[str, Any]: 작업 결과
    """
    logger.info("전자레인지 조리 중단 요청 수신")
    result = await mock_api_request("/api/microwave/stop", "POST")
    return result

@mcp.tool()
async def get_microwave_remaining_time() -> Dict[str, Any]:
    """
    전자레인지 조리 남은 시간을 조회합니다.
    
    Returns:
        Dict[str, Any]: 남은 시간 정보
    """
    logger.info("전자레인지 남은 시간 조회 요청 수신")
    result = await mock_api_request("/api/microwave/status")
    
    status = result
    if "remaining_seconds" in status:
        return {
            "remaining_seconds": status["remaining_seconds"],
            "cooking": status["cooking"],
            "message": status["message"]
        }
    else:
        return {
            "remaining_seconds": 0,
            "cooking": status["cooking"],
            "message": "조리 중이 아니거나 남은 시간 정보가 없습니다."
        }

if __name__ == "__main__":
    # 서버 시작 메시지 출력
    print("전자레인지 MCP 서버가 실행 중입니다...")
    
    # SSE 트랜스포트를 사용하여 MCP 서버 시작
    mcp.run(transport="sse") 