import json
import requests
import os
import logging
from typing import List, Dict, Any, Optional
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()
MOCK_SERVER_URL = os.environ.get("MOCK_SERVER_URL", "http://localhost:8000")

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("refrigerator_mcp_server")

# FastMCP 인스턴스 생성
mcp = FastMCP(
    "refrigerator",  # MCP 서버 이름
    instructions="냉장고를 제어하는 도구입니다. 식재료 조회/추가, 디스플레이 상태/내용 설정 등의 기능을 제공합니다.",
    host="0.0.0.0",  # 모든 IP에서 접속 허용
    port=8001,  # 포트 번호
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
async def get_food_items() -> Dict[str, Any]:
    """
    냉장고에 있는 식재료 목록을 조회합니다.
    
    Returns:
        Dict[str, Any]: 식재료 목록 (이름과 수량)
    """
    logger.info("냉장고 식재료 목록 조회 요청 수신")
    result = await mock_api_request("/refrigerator/food-items")
    return result

@mcp.tool()
async def add_food_item(name: str, quantity: str) -> Dict[str, Any]:
    """
    냉장고에 식재료를 추가합니다.
    
    Args:
        name (str): 식재료 이름
        quantity (str): 식재료 수량
        
    Returns:
        Dict[str, Any]: 작업 결과
    """
    logger.info(f"냉장고 식재료 추가 요청 수신: {name}, {quantity}")
    result = await mock_api_request("/refrigerator/food-items", "POST", {"name": name, "quantity": quantity})
    return result

@mcp.tool()
async def get_display_state() -> Dict[str, Any]:
    """
    냉장고 디스플레이 상태를 조회합니다.
    
    Returns:
        Dict[str, Any]: 디스플레이 상태 (켜짐/꺼짐)
    """
    logger.info("냉장고 디스플레이 상태 조회 요청 수신")
    result = await mock_api_request("/refrigerator/display-state")
    return result

@mcp.tool()
async def set_display_state(state: str) -> Dict[str, Any]:
    """
    냉장고 디스플레이 상태를 변경합니다.
    
    Args:
        state (str): 디스플레이 상태 ("디스플레이중" 또는 "디스플레이중아님")
        
    Returns:
        Dict[str, Any]: 작업 결과
    """
    logger.info(f"냉장고 디스플레이 상태 변경 요청 수신: {state}")
    if state not in ["디스플레이중", "디스플레이중아님"]:
        return {"error": "상태는 '디스플레이중' 또는 '디스플레이중아님' 이어야 합니다."}
    
    result = await mock_api_request("/refrigerator/display-state", "POST", {"state": state})
    return result

@mcp.tool()
async def set_display_content(content: str) -> Dict[str, Any]:
    """
    냉장고 디스플레이 내용을 설정합니다.
    
    Args:
        content (str): 표시할 내용
        
    Returns:
        Dict[str, Any]: 작업 결과
    """
    logger.info(f"냉장고 디스플레이 내용 설정 요청 수신: {content[:20]}...")
    result = await mock_api_request("/refrigerator/display-content", "POST", {"content": content})
    return result

@mcp.tool()
async def get_cooking_state() -> Dict[str, Any]:
    """
    냉장고 디스플레이 요리 상태를 조회합니다.
    
    Returns:
        Dict[str, Any]: 요리 상태 정보
    """
    logger.info("냉장고 요리 상태 조회 요청 수신")
    result = await mock_api_request("/refrigerator/cooking-state")
    return result

if __name__ == "__main__":
    # 서버 시작 메시지 출력
    print("냉장고 MCP 서버가 실행 중입니다...")
    
    # SSE 트랜스포트를 사용하여 MCP 서버 시작
    mcp.run(transport="sse") 