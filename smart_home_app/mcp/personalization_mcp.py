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
logger = logging.getLogger("personalization_mcp_server")

# FastMCP 인스턴스 생성
mcp = FastMCP(
    "personalization",  # MCP 서버 이름
    instructions="사용자 선호도 관리 기능을 제어하는 도구입니다. 선호도 조회/추가/삭제, 가전기기 목록 조회 등의 기능을 제공합니다.",
    host="0.0.0.0",  # 모든 IP에서 접속 허용
    port=8006,  # 포트 번호
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
        elif method.upper() == "DELETE":
            response = requests.delete(url)
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
async def get_preferences() -> Dict[str, Any]:
    """
    사용자의 개인 선호도 리스트를 조회합니다.
    
    Returns:
        Dict[str, Any]: 선호도 목록
    """
    logger.info("사용자 선호도 목록 조회 요청 수신")
    result = await mock_api_request("/personalization/preferences")
    return result

@mcp.tool()
async def add_preference(description: str) -> Dict[str, Any]:
    """
    사용자의 개인 선호도를 추가합니다.
    
    Args:
        description (str): 선호도 설명
        
    Returns:
        Dict[str, Any]: 작업 결과
    """
    logger.info(f"사용자 선호도 추가 요청 수신: {description}")
    result = await mock_api_request("/personalization/preferences", "POST", {"description": description})
    return result

@mcp.tool()
async def delete_preference(preference_id: int) -> Dict[str, Any]:
    """
    사용자의 개인 선호도를 삭제합니다.
    
    Args:
        preference_id (int): 삭제할 선호도 ID
        
    Returns:
        Dict[str, Any]: 작업 결과
    """
    logger.info(f"사용자 선호도 삭제 요청 수신: ID: {preference_id}")
    result = await mock_api_request(f"/personalization/preferences/{preference_id}", "DELETE")
    return result

@mcp.tool()
async def get_appliances() -> Dict[str, Any]:
    """
    사용자가 보유한 주방 가전기기 목록을 조회합니다.
    
    Returns:
        Dict[str, Any]: 가전기기 목록
    """
    logger.info("사용자 가전기기 목록 조회 요청 수신")
    result = await mock_api_request("/personalization/appliances")
    return result

@mcp.tool()
async def analyze_preferences() -> Dict[str, Any]:
    """
    사용자의 선호도를 분석하여 요약 정보를 제공합니다.
    
    Returns:
        Dict[str, Any]: 선호도 분석 결과
    """
    logger.info("사용자 선호도 분석 요청 수신")
    
    # 선호도 조회
    prefs_result = await mock_api_request("/personalization/preferences")
    if "error" in prefs_result:
        logger.error(f"선호도 정보 조회 실패: {prefs_result['error']}")
        return {"error": "선호도 정보를 가져오는데 실패했습니다."}
    
    preferences = prefs_result
    
    # 선호하는 음식 유형 분석
    food_preferences = []
    disliked_foods = []
    lifestyle_info = []
    
    for pref in preferences:
        desc = pref["description"].lower()
        if "좋아함" in desc:
            food_preferences.append(desc)
        elif "싫어함" in desc or "않음" in desc:
            disliked_foods.append(desc)
        else:
            lifestyle_info.append(desc)
    
    analysis_result = {
        "summary": {
            "favorite_foods": food_preferences,
            "disliked_foods": disliked_foods,
            "lifestyle": lifestyle_info
        },
        "total_preferences": len(preferences)
    }
    
    logger.info(f"선호도 분석 완료: {len(food_preferences)}개의 선호 음식, {len(disliked_foods)}개의 비선호 음식")
    return analysis_result

if __name__ == "__main__":
    # 서버 시작 메시지 출력
    print("선호도 관리 MCP 서버가 실행 중입니다...")
    
    # SSE 트랜스포트를 사용하여 MCP 서버 시작
    mcp.run(transport="sse") 