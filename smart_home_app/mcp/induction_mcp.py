from mcp.server.fastmcp import FastMCP
import os
import requests
import json
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()
MOCK_SERVER_URL = os.environ.get("MOCK_SERVER_URL", "http://localhost:8000")

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("induction_mcp_server")

# FastMCP 인스턴스 생성
mcp = FastMCP(
    "induction",  # MCP 서버 이름
    instructions="인덕션을 제어하는 도구입니다. 전원 상태 확인, 전원 상태 변경, 조리 시작 등의 기능을 제공합니다.",
    host="0.0.0.0",  # 모든 IP에서 접속 허용
    port=8002,  # 포트 번호
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
async def get_status() -> Dict[str, Any]:
    """
    인덕션 상태를 조회합니다. 
    전원 상태(켜짐/꺼짐), 조리 여부, 현재 화력 정보를 반환합니다.
    
    Returns:
        Dict[str, Any]: 인덕션 상태 정보
    """
    logger.info("인덕션 상태 조회 요청 수신")
    result = await mock_api_request("/api/induction/status")
    return result

@mcp.tool()
async def toggle_power() -> Dict[str, Any]:
    """
    인덕션 전원을 켜거나 끕니다.
    현재 전원 상태를 반대로 변경합니다. (켜져 있으면 끄고, 꺼져 있으면 켭니다)
    
    Returns:
        Dict[str, Any]: 작업 결과
    """
    logger.info("인덕션 전원 토글 요청 수신")
    result = await mock_api_request("/api/induction/power", "POST")
    return result

@mcp.tool()
async def start_cooking(heat_level: str) -> Dict[str, Any]:
    """
    인덕션 조리를 시작합니다.
    
    Args:
        heat_level (str): 화력 수준 ("강불", "중불", "약불" 중 하나)
        
    Returns:
        Dict[str, Any]: 작업 결과
    """
    logger.info(f"인덕션 조리 시작 요청 수신: 화력 {heat_level}")
    if heat_level not in ["강불", "중불", "약불"]:
        return {"error": "화력은 '강불', '중불', '약불' 중 하나여야 합니다."}
    
    result = await mock_api_request("/api/induction/start-cooking", "POST", {"heat_level": heat_level})
    return result

@mcp.tool()
async def stop_cooking() -> Dict[str, Any]:
    """
    인덕션 조리를 중단합니다.
    
    Returns:
        Dict[str, Any]: 작업 결과
    """
    logger.info("인덕션 조리 중단 요청 수신")
    result = await mock_api_request("/api/induction/stop-cooking", "POST")
    return result

if __name__ == "__main__":
    # 서버 시작 메시지 출력
    print("인덕션 MCP 서버가 실행 중입니다...")
    
    # SSE 트랜스포트를 사용하여 MCP 서버 시작
    mcp.run(transport="sse") 