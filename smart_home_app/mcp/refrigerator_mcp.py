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
REFRIGERATOR_MCP_NAME = os.environ.get("REFRIGERATOR_MCP_NAME", "refrigerator")
REFRIGERATOR_MCP_HOST = os.environ.get("REFRIGERATOR_MCP_HOST", "0.0.0.0")
REFRIGERATOR_MCP_PORT = int(os.environ.get("REFRIGERATOR_MCP_PORT", 10001))
REFRIGERATOR_MCP_INSTRUCTIONS = os.environ.get("REFRIGERATOR_MCP_INSTRUCTIONS", "냉장고를 제어하는 도구입니다. 식재료 조회/추가, 디스플레이 상태/내용 설정, 요리 상태 확인, 전체 냉장고 상태 조회 등의 기능을 제공합니다.")

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("refrigerator_mcp_server")

# FastMCP 인스턴스 생성
mcp = FastMCP(
    REFRIGERATOR_MCP_NAME,  # MCP 서버 이름
    instructions=REFRIGERATOR_MCP_INSTRUCTIONS,
    host=REFRIGERATOR_MCP_HOST,  # 모든 IP에서 접속 허용
    port=REFRIGERATOR_MCP_PORT,  # 포트 번호
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
async def get_refrigerator_status() -> Dict[str, Any]:
    """
    냉장고의 전체 상태를 조회합니다.
    
    이 도구는 냉장고의 현재 식재료 목록, 디스플레이 상태, 요리 상태, 문 상태, 온도 설정 등 
    냉장고의 전반적인 상태 정보를 한 번에 조회합니다.
    
    Returns:
        Dict[str, Any]: 냉장고 전체 상태 정보를 포함하는 딕셔너리 형태의 응답
        
    응답에 포함되는 정보:
        - food_items_count: 냉장고에 있는 총 식재료 수
        - food_categories: 카테고리별 식재료 수량
        - food_items: 식재료 목록(일부)
        - display_state: 디스플레이 상태 ("on" 또는 "off")
        - display_content: 디스플레이에 표시된 내용
        - cooking_state: 요리 상태 ("요리중" 또는 "대기중")
        - door_status: 문 상태 ("open" 또는 "closed")
        - temperature: 냉장/냉동실 온도 설정
        - message: 냉장고 상태를 설명하는 메시지
        
    예시 응답:
        {
            "food_items_count": 7,
            "food_categories": {"육류": 1, "채소": 2, "유제품": 2, "기타": 2},
            "food_items": [
                {"name": "계란", "quantity": "10개", "category": "기타"},
                {"name": "소고기", "quantity": "500g", "category": "육류"}
            ],
            "display_state": "on",
            "display_content": "오늘의 추천 요리: 비프 스테이크",
            "cooking_state": "대기중",
            "door_status": "closed",
            "temperature": {"fridge": 3, "freezer": -18},
            "message": "현재 7개 식재료가 보관 중입니다. 디스플레이가 켜져 있고 추천 요리를 표시 중입니다."
        }
    """
    logger.info("냉장고 전체 상태 조회 요청 수신")
    result = await mock_api_request("/refrigerator/status")
    return result

@mcp.tool()
async def get_food_items() -> Dict[str, Any]:
    """
    냉장고에 있는 식재료 목록을 조회합니다.
    
    이 도구는 현재 냉장고에 보관 중인 모든 식재료의 목록을 반환합니다.
    각 식재료의 이름, 수량, 유통기한, 카테고리 등의 정보를 포함합니다.
    
    Returns:
        Dict[str, Any]: 식재료 목록 정보를 포함하는 딕셔너리 형태의 응답
            - items: 식재료 객체의 배열
            - total_count: 전체 식재료 개수
    
    식재료 객체 구조:
        - name: 식재료 이름 (예: "계란", "우유", "소고기" 등)
        - quantity: 수량 정보 (예: "500g", "1개", "2팩" 등)
        - expiry_date: 유통기한 (선택적, 예: "2023-12-31")
        - category: 카테고리 (선택적, 예: "육류", "유제품", "채소" 등)
    
    예시 응답:
        {
            "items": [
                {"name": "계란", "quantity": "10개", "category": "유제품", "expiry_date": "2023-12-15"},
                {"name": "우유", "quantity": "1L", "category": "유제품", "expiry_date": "2023-12-10"},
                {"name": "소고기", "quantity": "500g", "category": "육류", "expiry_date": "2023-12-05"},
                {"name": "당근", "quantity": "3개", "category": "채소"}
            ],
            "total_count": 4
        }
    """
    logger.info("냉장고 식재료 목록 조회 요청 수신")
    result = await mock_api_request("/refrigerator/food-items")
    return result

@mcp.tool()
async def add_food_item(name: str, quantity: str, expiry_date: Optional[str] = None, category: Optional[str] = None) -> Dict[str, Any]:
    """
    냉장고에 새로운 식재료를 추가합니다.
    
    이 도구는 지정된 식재료 정보를 냉장고에 추가합니다. 식재료 이름과 수량은 필수이며,
    유통기한과 카테고리는 선택적으로 지정할 수 있습니다.
    
    Args:
        name (str): 식재료 이름 (예: "계란", "우유", "소고기" 등)
        quantity (str): 수량 정보 (예: "500g", "1개", "2팩" 등)
        expiry_date (Optional[str]): 유통기한. "YYYY-MM-DD" 형식 (예: "2023-12-31")
        category (Optional[str]): 식재료 카테고리 (예: "육류", "유제품", "채소" 등)
        
    Returns:
        Dict[str, Any]: 식재료 추가 결과를 포함하는 딕셔너리 형태의 응답
            - result: 작업 결과 상태 ("success", "error" 등)
            - message: 결과 설명 메시지
    
    예시:
        add_food_item("당근", "3개", "2023-12-20", "채소")
        add_food_item("우유", "1L", "2023-12-10", "유제품")
        add_food_item("소고기", "500g") -> 유통기한과 카테고리 없이 추가
    
    예시 응답 (성공 시):
        {
            "result": "success",
            "message": "식재료 '당근'이 성공적으로 추가되었습니다."
        }
    """
    logger.info(f"냉장고 식재료 추가 요청 수신: {name}, {quantity}")
    
    # 요청 데이터 구성
    request_data = {
        "name": name,
        "quantity": quantity
    }
    
    if expiry_date:
        request_data["expiry_date"] = expiry_date
    
    if category:
        request_data["category"] = category
    
    result = await mock_api_request("/refrigerator/food-items", "POST", request_data)
    return result

@mcp.tool()
async def get_display_state() -> Dict[str, Any]:
    """
    냉장고 디스플레이의 현재 상태를 조회합니다.
    
    이 도구는 냉장고 외부 디스플레이의 상태(켜짐/꺼짐)와 현재 표시되고 있는 내용을 반환합니다.
    
    Returns:
        Dict[str, Any]: 디스플레이 상태 정보를 포함하는 딕셔너리 형태의 응답
            - state: 디스플레이 상태 ("on" 또는 "off")
            - content: 현재 표시되고 있는 내용
            - message: 상태 설명 메시지
    
    예시 응답 (켜져 있을 때):
        {
            "state": "on",
            "content": "오늘의 추천 요리: 비프 스테이크",
            "message": "냉장고 디스플레이가 켜져 있으며 '오늘의 추천 요리: 비프 스테이크'를 표시하고 있습니다."
        }
    
    예시 응답 (꺼져 있을 때):
        {
            "state": "off",
            "content": "",
            "message": "냉장고 디스플레이가 꺼져 있습니다."
        }
    """
    logger.info("냉장고 디스플레이 상태 조회 요청 수신")
    result = await mock_api_request("/refrigerator/display-state")
    return result

@mcp.tool()
async def set_display_state(state: str) -> Dict[str, Any]:
    """
    냉장고 디스플레이 상태를 변경합니다.
    
    이 도구는 냉장고 외부 디스플레이를 켜거나 끕니다.
    
    Args:
        state (str): 설정할 디스플레이 상태. 다음 값들만 허용됩니다:
            - "on": 디스플레이를 켭니다.
            - "off": 디스플레이를 끕니다.
        
    Returns:
        Dict[str, Any]: 디스플레이 상태 변경 결과를 포함하는 딕셔너리 형태의 응답
            - result: 작업 결과 상태 ("success", "error" 등)
            - message: 결과 설명 메시지
    
    예시:
        set_display_state("on") -> 디스플레이를 켭니다.
        set_display_state("off") -> 디스플레이를 끕니다.
    
    예시 응답:
        {
            "result": "success",
            "message": "냉장고 디스플레이가 켜졌습니다."
        }
    """
    logger.info(f"냉장고 디스플레이 상태 변경 요청 수신: {state}")
    if state not in ["on", "off"]:
        return {"error": "상태는 'on' 또는 'off'여야 합니다."}
    
    result = await mock_api_request("/refrigerator/display-state", "POST", {"state": state})
    return result

@mcp.tool()
async def set_display_content(content: str) -> Dict[str, Any]:
    """
    냉장고 디스플레이에 표시할 내용을 설정합니다.
    
    이 도구는 냉장고 외부 디스플레이에 표시할 내용을 설정합니다.
    디스플레이가 켜져 있을 때만 내용이 실제로 표시됩니다.
    
    Args:
        content (str): 디스플레이에 표시할 내용. 텍스트만 지원됩니다.
        
    Returns:
        Dict[str, Any]: 디스플레이 내용 설정 결과를 포함하는 딕셔너리 형태의 응답
            - result: 작업 결과 상태 ("success", "error" 등)
            - message: 결과 설명 메시지
    
    예시:
        set_display_content("오늘의 추천 요리: 비프 스테이크")
        set_display_content("냉장고 문이 열려있습니다.")
    
    예시 응답:
        {
            "result": "success",
            "message": "냉장고 디스플레이 내용이 설정되었습니다."
        }
    
    참고:
        디스플레이가 꺼져 있는 경우 내용이 설정되더라도 표시되지 않습니다.
        먼저 set_display_state("on")을 호출하여 디스플레이를 켜야 합니다.
    """
    logger.info(f"냉장고 디스플레이 내용 설정 요청 수신: {content[:20]}...")
    result = await mock_api_request("/refrigerator/display-content", "POST", {"content": content})
    return result

@mcp.tool()
async def get_cooking_state() -> Dict[str, Any]:
    """
    냉장고 디스플레이의 요리 상태를 조회합니다.
    
    이 도구는 냉장고 디스플레이에 표시된 현재 요리 과정의 상태와 단계 정보를 반환합니다.
    
    Returns:
        Dict[str, Any]: 요리 상태 정보를 포함하는 딕셔너리 형태의 응답
            - state: 요리 상태 ("요리중" 또는 "대기중")
            - step_info: 현재 요리 단계 정보
            - message: 상태 설명 메시지
    
    예시 응답 (요리 중일 때):
        {
            "state": "요리중",
            "step_info": "소고기를 중불에 5분간 구워주세요.",
            "message": "현재 요리 단계: 소고기를 중불에 5분간 구워주세요."
        }
    
    예시 응답 (대기 중일 때):
        {
            "state": "대기중",
            "step_info": "",
            "message": "요리가 진행 중이 아닙니다."
        }
    """
    logger.info("냉장고 요리 상태 조회 요청 수신")
    result = await mock_api_request("/refrigerator/cooking-state")
    return result

@mcp.tool()
async def set_cooking_state(step_info: str) -> Dict[str, Any]:
    """
    냉장고 디스플레이에 현재 요리 단계 정보를 설정합니다.
    
    이 도구는 냉장고 디스플레이에 표시될 요리 단계 정보를 설정합니다.
    단계 정보가 설정되면 요리 상태가 "요리중"으로 변경됩니다.
    
    Args:
        step_info (str): 표시할 요리 단계 정보
        
    Returns:
        Dict[str, Any]: 요리 상태 설정 결과를 포함하는 딕셔너리 형태의 응답
            - result: 작업 결과 상태 ("success", "error" 등)
            - message: 결과 설명 메시지
    
    예시:
        set_cooking_state("당근을 깍둑썰기로 자르세요.")
        set_cooking_state("소고기를 중불에 5분간 구워주세요.")
    
    예시 응답:
        {
            "result": "success",
            "message": "요리 단계가 설정되었습니다: 당근을 깍둑썰기로 자르세요."
        }
    
    참고:
        설정된 단계 정보는 냉장고 디스플레이가 켜져 있을 때만 표시됩니다.
        빈 문자열을 전달하면 요리 상태가 "대기중"으로 변경됩니다.
    """
    logger.info(f"냉장고 요리 단계 설정 요청 수신: {step_info}")
    result = await mock_api_request("/refrigerator/cooking-state", "POST", {"step_info": step_info})
    return result

if __name__ == "__main__":
    # 서버 시작 메시지 출력
    print("냉장고 MCP 서버가 실행 중입니다...")
    
    # SSE 트랜스포트를 사용하여 MCP 서버 시작
    mcp.run(transport="sse") 