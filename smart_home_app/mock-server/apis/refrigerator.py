from fastapi import APIRouter, HTTPException
from models.refrigerator import (
    FoodItem, FoodItemCreate, FoodItemsResponse, ResultResponse,
    StepInfoRequest, CookingStateResponse, DisplayStateResponse,
    DisplayStateRequest, DisplayContentRequest
)
from services import refrigerator_service
from logging_config import setup_logger

# 로거 설정
logger = setup_logger("refrigerator_api")

router = APIRouter(
    prefix="/refrigerator",
    tags=["Refrigerator"],
    responses={404: {"description": "Not found"}},
)

@router.get("/food-items", response_model=FoodItemsResponse)
async def get_food_items():
    """냉장고에 있는 식재료 리스트 조회"""
    logger.info("API 호출: 냉장고에 있는 식재료 리스트 조회")
    return refrigerator_service.get_food_items()

@router.post("/food-items", response_model=ResultResponse)
async def add_food_item(food_item: FoodItemCreate):
    """냉장고에 식재료 추가"""
    logger.info(f"API 호출: 냉장고에 식재료 추가 ({food_item.name}, {food_item.quantity})")
    return refrigerator_service.add_food_item(food_item)

@router.get("/cooking-state", response_model=CookingStateResponse)
async def get_cooking_state():
    """냉장고 디스플레이 요리 상태 조회"""
    logger.info("API 호출: 냉장고 디스플레이 요리 상태 조회")
    return refrigerator_service.get_cooking_state()

@router.post("/cooking-state", response_model=ResultResponse)
async def set_cooking_state(request: StepInfoRequest):
    """냉장고 디스플레이에 레시피 스텝 정보 설정"""
    logger.info(f"API 호출: 냉장고 디스플레이에 레시피 스텝 정보 설정")
    return refrigerator_service.set_cooking_state(request.step_info)

@router.get("/display-state", response_model=DisplayStateResponse)
async def get_display_state():
    """냉장고 디스플레이 상태 조회"""
    logger.info("API 호출: 냉장고 디스플레이 상태 조회")
    return refrigerator_service.get_display_state()

@router.post("/display-state", response_model=ResultResponse)
async def set_display_state(request: DisplayStateRequest):
    """냉장고 디스플레이 상태 변경"""
    logger.info(f"API 호출: 냉장고 디스플레이 상태 변경 ({request.state})")
    return refrigerator_service.set_display_state(request)

@router.post("/display-content", response_model=ResultResponse)
async def set_display_content(request: DisplayContentRequest):
    """냉장고 디스플레이 내용 설정"""
    logger.info(f"API 호출: 냉장고 디스플레이 내용 설정 (내용: {request.content})")
    return refrigerator_service.set_display_content(request) 