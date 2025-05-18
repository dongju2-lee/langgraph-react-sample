from fastapi import APIRouter, HTTPException
from models.refrigerator import (
    FoodItem, FoodItemCreate, FoodItemsResponse, ResultResponse,
    StepInfoRequest, CookingStateResponse, DisplayStateResponse,
    DisplayStateRequest, DisplayContentRequest
)
from services import refrigerator_service
from logging_config import setup_logger
from typing import Dict, Any

# 로거 설정
logger = setup_logger("refrigerator_api")

router = APIRouter(
    prefix="/refrigerator",
    tags=["Refrigerator"],
    responses={404: {"description": "Not found"}},
)

@router.get("/status", response_model=Dict[str, Any])
async def get_status():
    """
    냉장고 전체 상태 조회
    
    - 요청 본문이 필요 없습니다.
    - 예시 요청: GET /refrigerator/status
    - 현재 냉장고의 전반적인 상태 정보(식재료 목록, 디스플레이 상태, 요리 상태 등)를 조회합니다.
    - 응답에는 food_items_count(식재료 수), display_state(디스플레이 상태), cooking_state(요리 상태) 정보가 포함됩니다.
    """
    logger.info("API 호출: 냉장고 전체 상태 조회")
    try:
        return refrigerator_service.get_status()
    except Exception as e:
        logger.exception("냉장고 상태 조회 실패")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/food-items", response_model=FoodItemsResponse)
async def get_food_items():
    """
    냉장고에 있는 식재료 리스트 조회
    
    - 요청 본문이 필요 없습니다.
    - 예시 요청: GET /refrigerator/food-items
    - 현재 냉장고에 있는 모든 식재료 목록을 반환합니다.
    """
    logger.info("API 호출: 냉장고에 있는 식재료 리스트 조회")
    return refrigerator_service.get_food_items()

@router.post("/food-items", response_model=ResultResponse)
async def add_food_item(food_item: FoodItemCreate):
    """
    냉장고에 식재료 추가
    
    - name: 식재료 이름 (문자열)
    - quantity: 식재료 수량 (문자열, 예: "1개", "500g")
    - expiry_date: 유통기한 (선택 사항, 문자열, 예: "2023-12-31")
    - category: 식재료 카테고리 (선택 사항, 문자열, 예: "육류", "채소")
    - 예시: { "name": "당근", "quantity": "3개", "expiry_date": "2023-12-31", "category": "채소" }
    - 지정한 식재료를 냉장고에 추가합니다.
    """
    logger.info(f"API 호출: 냉장고에 식재료 추가 ({food_item.name}, {food_item.quantity})")
    return refrigerator_service.add_food_item(food_item)

@router.get("/cooking-state", response_model=CookingStateResponse)
async def get_cooking_state():
    """
    냉장고 디스플레이 요리 상태 조회
    
    - 요청 본문이 필요 없습니다.
    - 예시 요청: GET /refrigerator/cooking-state
    - 현재 냉장고 디스플레이에 표시된 요리 상태 정보를 반환합니다.
    """
    logger.info("API 호출: 냉장고 디스플레이 요리 상태 조회")
    return refrigerator_service.get_cooking_state()

@router.post("/cooking-state", response_model=ResultResponse)
async def set_cooking_state(request: StepInfoRequest):
    """
    냉장고 디스플레이에 레시피 스텝 정보 설정
    
    - step_info: 레시피 스텝 정보 (문자열)
    - 예시: { "step_info": "당근을 깍둑썰기로 자르세요." }
    - 냉장고 디스플레이에 현재 요리 단계 정보를 설정합니다.
    """
    logger.info(f"API 호출: 냉장고 디스플레이에 레시피 스텝 정보 설정")
    return refrigerator_service.set_cooking_state(request.step_info)

@router.get("/display-state", response_model=DisplayStateResponse)
async def get_display_state():
    """
    냉장고 디스플레이 상태 조회
    
    - 요청 본문이 필요 없습니다.
    - 예시 요청: GET /refrigerator/display-state
    - 현재 냉장고 디스플레이의 상태(켜짐/꺼짐)와 표시된 내용을 반환합니다.
    """
    logger.info("API 호출: 냉장고 디스플레이 상태 조회")
    return refrigerator_service.get_display_state()

@router.post("/display-state", response_model=ResultResponse)
async def set_display_state(request: DisplayStateRequest):
    """
    냉장고 디스플레이 상태 변경
    
    - state: 디스플레이 상태 ("on" 또는 "off")
    - 예시: { "state": "on" }
    - 냉장고 디스플레이 화면을 켜거나 끕니다.
    """
    logger.info(f"API 호출: 냉장고 디스플레이 상태 변경 ({request.state})")
    return refrigerator_service.set_display_state(request)

@router.post("/display-content", response_model=ResultResponse)
async def set_display_content(request: DisplayContentRequest):
    """
    냉장고 디스플레이 내용 설정
    
    - content: 디스플레이에 표시할 내용 (문자열)
    - 예시: { "content": "오늘의 레시피: 당근 샐러드" }
    - 냉장고 디스플레이에 표시할 내용을 설정합니다.
    """
    logger.info(f"API 호출: 냉장고 디스플레이 내용 설정 (내용: {request.content})")
    return refrigerator_service.set_display_content(request) 