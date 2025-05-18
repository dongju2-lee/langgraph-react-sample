from mcp.server.fastmcp import FastMCP
import os
import requests
import json
import logging
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()
MOCK_SERVER_URL = os.environ.get("MOCK_SERVER_URL", "http://localhost:10000")
COOKING_MCP_NAME = os.environ.get("COOKING_MCP_NAME", "cooking")
COOKING_MCP_HOST = os.environ.get("COOKING_MCP_HOST", "0.0.0.0")
COOKING_MCP_PORT = int(os.environ.get("COOKING_MCP_PORT", 10005))
COOKING_MCP_INSTRUCTIONS = os.environ.get("COOKING_MCP_INSTRUCTIONS", "요리 관련 기능을 제어하는 도구입니다. 식재료 기반 요리 추천, 레시피 조회, 요리 시작, 가능한 레시피 확인 등의 기능을 제공합니다.")

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("cooking_mcp_server")

# FastMCP 인스턴스 생성
mcp = FastMCP(
    COOKING_MCP_NAME,  # MCP 서버 이름
    instructions=COOKING_MCP_INSTRUCTIONS,
    host=COOKING_MCP_HOST,  # 모든 IP에서 접속 허용
    port=COOKING_MCP_PORT,  # 포트 번호
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
async def recommend_food(ingredients: List[str]) -> Dict[str, Any]:
    """
    식재료를 기반으로 요리를 추천합니다.
    
    Args:
        ingredients (List[str]): 보유한 식재료 목록. 예: ["소고기", "양파", "당근"]
        
    Returns:
        Dict[str, Any]: 추천된 음식 정보를 포함하는 딕셔너리
        
    예시 요청:
        recommend_food(ingredients=["소고기", "양파", "당근"])
        
    예시 응답:
        {
            "recommended_foods": [
                {
                    "name": "소고기 볶음밥",
                    "confidence": 0.95,
                    "missing_ingredients": []
                },
                {
                    "name": "소고기 카레",
                    "confidence": 0.80,
                    "missing_ingredients": ["카레가루"]
                }
            ],
            "message": "2개의 요리가 추천되었습니다."
        }
        
    오류 응답:
        {
            "error": "식재료 목록이 비어 있습니다."
        }
    """
    logger.info(f"식재료 기반 요리 추천 요청 수신: 재료: {ingredients}")
    result = await mock_api_request("/api/cooking/recommend", "POST", ingredients)
    return result

@mcp.tool()
async def get_recipe(food_name: str) -> Dict[str, Any]:
    """
    음식 이름을 기반으로 레시피를 조회합니다.
    
    Args:
        food_name (str): 음식 이름. 대소문자를 구분하며 정확한 이름을 입력해야 합니다.
        
    Returns:
        Dict[str, Any]: 레시피 정보를 포함하는 딕셔너리
        
    예시 요청:
        get_recipe(food_name="소고기 볶음밥")
        
    예시 응답:
        {
            "name": "소고기 볶음밥",
            "difficulty": "중급",
            "cooking_time": "30분",
            "ingredients": [
                {"name": "소고기", "amount": "200g"},
                {"name": "양파", "amount": "1개"},
                {"name": "당근", "amount": "1/2개"},
                {"name": "밥", "amount": "2공기"}
            ],
            "steps": [
                {"step": 1, "description": "소고기를 손질하고 양념합니다.", "time": "5분"},
                {"step": 2, "description": "야채를 잘게 썹니다.", "time": "5분"},
                {"step": 3, "description": "팬에 소고기를 먼저 볶습니다.", "time": "7분"},
                {"step": 4, "description": "야채를 넣고 함께 볶습니다.", "time": "5분"},
                {"step": 5, "description": "밥을 넣고 고루 볶아줍니다.", "time": "8분"}
            ]
        }
        
    오류 응답:
        {
            "error": "해당 음식의 레시피를 찾을 수 없습니다."
        }
    """
    logger.info(f"레시피 조회 요청 수신: 음식: {food_name}")
    result = await mock_api_request(f"/api/cooking/recipe/{food_name}")
    
    if "error" in result:
        logger.error(f"레시피 조회 실패: {result['error']}")
        
    return result

@mcp.tool()
async def get_available_foods() -> List[str]:
    """
    현재 레시피가 제공되는 모든 음식 목록을 반환합니다.
    이 목록은 사용자가 조리할 수 있는 요리의 선택지를 제공합니다.
    
    Args:
        없음
        
    Returns:
        List[str]: 이용 가능한 음식 목록을 문자열 배열로 반환
        
    예시 요청:
        get_available_foods()
        
    예시 응답:
        [
            "라자냐", 
            "고구마튀김", 
            "오징어볶음", 
            "소고기 볶음밥", 
            "닭볶음탕"
        ]
    """
    logger.info("이용 가능한 음식 목록 조회 요청 수신")
    # 냉장고에 있는 재료들로 추천 가능한 요리 목록을 가져옴
    recipes = [
        "라자냐", "고구마튀김", "오징어볶음", "소고기 볶음밥", "닭볶음탕"
    ]
    return recipes

@mcp.tool()
async def cook_recipe(food_name: str) -> Dict[str, Any]:
    """
    요리를 시작합니다. 해당 요리의 레시피를 조회하고 냉장고 디스플레이에 표시합니다.
    이 기능은 스마트 냉장고 디스플레이와 연동되어 요리 과정을 안내합니다.
    
    Args:
        food_name (str): 요리할 음식 이름. 정확한 이름을 입력해야 하며, get_available_foods()로 
                         조회 가능한 음식 중 하나여야 합니다.
        
    Returns:
        Dict[str, Any]: 요리 시작 결과와 레시피 정보를 포함하는 딕셔너리
        
    예시 요청:
        cook_recipe(food_name="소고기 볶음밥")
        
    예시 응답:
        {
            "result": "success",
            "message": "소고기 볶음밥 요리를 시작합니다. 냉장고 디스플레이에 레시피가 표시됩니다.",
            "recipe": {
                "name": "소고기 볶음밥",
                "difficulty": "중급",
                "cooking_time": "30분",
                "ingredients": [
                    {"name": "소고기", "amount": "200g"},
                    {"name": "양파", "amount": "1개"},
                    {"name": "당근", "amount": "1/2개"},
                    {"name": "밥", "amount": "2공기"}
                ],
                "steps": [
                    {"step": 1, "description": "소고기를 손질하고 양념합니다.", "time": "5분"},
                    {"step": 2, "description": "야채를 잘게 썹니다.", "time": "5분"},
                    {"step": 3, "description": "팬에 소고기를 먼저 볶습니다.", "time": "7분"},
                    {"step": 4, "description": "야채를 넣고 함께 볶습니다.", "time": "5분"},
                    {"step": 5, "description": "밥을 넣고 고루 볶아줍니다.", "time": "8분"}
                ]
            }
        }
        
    오류 응답:
        {
            "error": "해당 음식의 레시피를 찾을 수 없습니다."
        }
    """
    logger.info(f"요리 시작 요청 수신: 음식: {food_name}")
    
    # 1. 레시피 조회
    recipe_result = await mock_api_request(f"/api/cooking/recipe/{food_name}")
    if "error" in recipe_result:
        logger.error(f"레시피 조회 실패: {recipe_result['error']}")
        return {"error": "해당 음식의 레시피를 찾을 수 없습니다."}
    
    # 2. 냉장고 디스플레이에 요리 정보 표시
    display_data = {
        "content": f"요리 시작: {food_name}\n첫 번째 단계: {recipe_result['steps'][0]['description']}"
    }
    display_result = await mock_api_request("/refrigerator/display-content", "POST", display_data)
    
    # 3. 냉장고 디스플레이 켜기
    state_data = {"state": "디스플레이중"}
    state_result = await mock_api_request("/refrigerator/display-state", "POST", state_data)
    
    return {
        "result": "success",
        "message": f"{food_name} 요리를 시작합니다. 냉장고 디스플레이에 레시피가 표시됩니다.",
        "recipe": recipe_result
    }

if __name__ == "__main__":
    # 서버 시작 메시지 출력
    print("요리 MCP 서버가 실행 중입니다...")
    
    # SSE 트랜스포트를 사용하여 MCP 서버 시작
    mcp.run(transport="sse") 