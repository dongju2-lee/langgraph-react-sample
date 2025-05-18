import json
import requests
import os
import logging
from typing import List, Dict, Any, Optional
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()
MOCK_SERVER_URL = os.environ.get("MOCK_SERVER_URL", "http://localhost:10000")
PERSONALIZATION_MCP_NAME = os.environ.get("PERSONALIZATION_MCP_NAME", "personalization")
PERSONALIZATION_MCP_HOST = os.environ.get("PERSONALIZATION_MCP_HOST", "0.0.0.0")
PERSONALIZATION_MCP_PORT = int(os.environ.get("PERSONALIZATION_MCP_PORT", 10006))
PERSONALIZATION_MCP_INSTRUCTIONS = os.environ.get("PERSONALIZATION_MCP_INSTRUCTIONS", "사용자 선호도 관리 기능을 제어하는 도구입니다. 선호도 조회/추가/삭제, 가전기기 목록 조회, 선호도 분석 등의 기능을 제공합니다.")

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("personalization_mcp_server")

# FastMCP 인스턴스 생성
mcp = FastMCP(
    PERSONALIZATION_MCP_NAME,  # MCP 서버 이름
    instructions=PERSONALIZATION_MCP_INSTRUCTIONS,
    host=PERSONALIZATION_MCP_HOST,  # 모든 IP에서 접속 허용
    port=PERSONALIZATION_MCP_PORT,  # 포트 번호
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
    
    이 도구는 사용자가 이전에 설정한 모든 개인 선호도 정보를 조회합니다.
    선호도 정보는 식품, 조리법, 생활 습관 등 다양한 카테고리를 포함할 수 있습니다.
    
    Returns:
        Dict[str, Any]: 사용자 선호도 목록을 포함하는 응답
    
    응답 구조:
        선호도 객체의 배열, 각 객체는 다음 필드를 포함합니다:
        - id: 선호도 ID (정수)
        - category: 선호도 카테고리 (문자열, 예: "식재료", "조리법", "음식 종류")
        - description: 선호도 세부 설명 (문자열, 예: "매운 음식 선호", "채식 요리 선호")
    
    예시 응답:
        [
            {
                "id": 1,
                "category": "식재료",
                "description": "매운 음식 선호"
            },
            {
                "id": 2,
                "category": "조리법",
                "description": "튀김 요리 선호하지 않음"
            },
            {
                "id": 3,
                "category": "음식 종류",
                "description": "한식 좋아함"
            }
        ]
    
    참고:
        선호도가 없는 경우 빈 배열([])이 반환될 수 있습니다.
        선호도 정보는 요리 추천 및 레시피 제안 시 활용됩니다.
    """
    logger.info("사용자 선호도 목록 조회 요청 수신")
    result = await mock_api_request("/personalization/preferences")
    return result

@mcp.tool()
async def add_preference(category: str, description: str) -> Dict[str, Any]:
    """
    사용자의 새로운 개인 선호도를 추가합니다.
    
    이 도구는 사용자의 식품, 조리법, 음식 종류 등에 대한 새로운 선호도 정보를 시스템에 추가합니다.
    추가된 선호도는 향후 개인화된 요리 추천 및 레시피 제안에 활용됩니다.
    
    Args:
        category (str): 선호도 카테고리 (예: "식재료", "조리법", "음식 종류")
        description (str): 선호도에 대한 구체적인 설명 (예: "매운 음식 선호", "채식 요리 선호")
        
    Returns:
        Dict[str, Any]: 작업 결과를 포함하는 딕셔너리 형태의 응답
            - result: 작업 결과 상태 ("success", "error" 등)
            - message: 결과 설명 메시지
            - preference_id: 추가된 선호도의 ID (선택적)
    
    예시:
        add_preference("식재료", "매운 음식 선호")
        add_preference("조리법", "튀김 요리 선호하지 않음")
        add_preference("음식 종류", "한식 좋아함")
    
    예시 응답 (성공 시):
        {
            "result": "success",
            "message": "선호도가 성공적으로 추가되었습니다",
            "preference_id": 4
        }
    
    예시 응답 (오류 시):
        {
            "result": "error",
            "message": "선호도 추가에 실패했습니다"
        }
    """
    logger.info(f"사용자 선호도 추가 요청 수신: {category} - {description}")
    result = await mock_api_request("/personalization/preferences", "POST", {
        "category": category,
        "description": description
    })
    return result

@mcp.tool()
async def delete_preference(preference_id: int) -> Dict[str, Any]:
    """
    사용자의 특정 개인 선호도를 삭제합니다.
    
    이 도구는 사용자가 이전에 설정한 선호도 중 지정된 ID를 가진 선호도를 시스템에서 제거합니다.
    더 이상 필요 없거나 변경된 선호도를 관리하는 데 사용됩니다.
    
    Args:
        preference_id (int): 삭제할 선호도의 고유 ID
        
    Returns:
        Dict[str, Any]: 작업 결과를 포함하는 딕셔너리 형태의 응답
            - result: 작업 결과 상태 ("success", "error" 등)
            - message: 결과 설명 메시지
    
    예시:
        delete_preference(4) -> ID가 4인 선호도를 삭제합니다
    
    예시 응답 (성공 시):
        {
            "result": "success",
            "message": "ID 4번 선호도가 성공적으로 삭제되었습니다"
        }
    
    예시 응답 (해당 ID가 없을 때):
        {
            "result": "error",
            "message": "ID 4번 선호도를 찾을 수 없습니다"
        }
    
    참고:
        존재하지 않는 ID를 삭제하려고 하면 오류가 반환됩니다.
        제거된 선호도는 복구할 수 없으니 신중하게 사용해야 합니다.
    """
    logger.info(f"사용자 선호도 삭제 요청 수신: ID: {preference_id}")
    result = await mock_api_request(f"/personalization/preferences/{preference_id}", "DELETE")
    return result

@mcp.tool()
async def get_appliances() -> Dict[str, Any]:
    """
    사용자가 보유한 주방 가전기기 목록을 조회합니다.
    
    이 도구는 사용자가 집에 보유하고 있는 모든 주방 가전기기의 목록을 반환합니다.
    각 가전기기의 종류, 모델명, 기능 등의 정보를 포함하며, 이 정보는 요리 추천 및
    레시피 제안 시 조리 방법을 사용자의 환경에 맞게 조정하는 데 사용됩니다.
    
    Returns:
        Dict[str, Any]: 가전기기 정보를 포함하는 딕셔너리 형태의 응답
            - appliances: 가전기기 객체의 배열
    
    가전기기 객체 구조:
        - name: 가전기기 이름 (예: "냉장고", "오븐", "전자레인지")
        - brand: 제조사 (예: "삼성", "LG", "위니아")
        - model: 모델명
        - features: 주요 기능 목록
    
    예시 응답:
        {
            "appliances": [
                {
                    "name": "냉장고",
                    "brand": "삼성",
                    "model": "RF85M91C1AP",
                    "features": ["김치 보관", "음성 인식", "스마트폰 연동"]
                },
                {
                    "name": "전자레인지",
                    "brand": "LG",
                    "model": "MW25R",
                    "features": ["자동 조리", "해동", "그릴"]
                },
                {
                    "name": "인덕션",
                    "brand": "위니아",
                    "model": "IH-531",
                    "features": ["3구 화구", "타이머", "보온 기능"]
                }
            ]
        }
    
    참고:
        이 정보는 요리사 에이전트가 사용자의 가전기기 환경에 맞는 조리법을 제안하는 데 활용됩니다.
        가전기기 정보는 사용자가 스마트홈 시스템에 등록한 정보를 기반으로 합니다.
    """
    logger.info("사용자 가전기기 목록 조회 요청 수신")
    result = await mock_api_request("/personalization/appliances")
    return result

@mcp.tool()
async def analyze_preferences() -> Dict[str, Any]:
    """
    사용자의 선호도를 분석하여 요약 정보를 제공합니다.
    
    이 도구는 사용자가 이전에 설정한 모든 선호도를 분석하여 식품 선호도, 비선호 식품,
    생활 습관 등으로 분류한 요약 정보를 제공합니다. 이 정보는 개인화된 요리 추천,
    건강 조언 등에 활용될 수 있습니다.
    
    Returns:
        Dict[str, Any]: 선호도 분석 결과를 포함하는 딕셔너리 형태의 응답
            - summary: 카테고리별 선호도 요약 정보
                - favorite_foods: 선호하는 음식 목록
                - disliked_foods: 선호하지 않는 음식 목록
                - lifestyle: 생활 습관 관련 선호도 목록
            - total_preferences: 전체 선호도 수
    
    예시 응답:
        {
            "summary": {
                "favorite_foods": ["매운 음식 좋아함", "한식 좋아함", "해산물 좋아함"],
                "disliked_foods": ["튀김 요리 싫어함", "너무 짠 음식 싫어함"],
                "lifestyle": ["아침에 커피 마심", "저녁은 가볍게 먹음"]
            },
            "total_preferences": 7
        }
    
    참고:
        분석은 선호도 설명에 포함된 키워드("좋아함", "싫어함", "않음" 등)를 기반으로 수행됩니다.
        선호도가 없는 경우 빈 목록이 반환될 수 있습니다.
        이 분석 결과는 에이전트가 사용자에게 더 개인화된 제안을 제공하는 데 도움이 됩니다.
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