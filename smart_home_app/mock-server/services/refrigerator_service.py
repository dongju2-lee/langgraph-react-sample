from models.refrigerator import (
    FoodItem, FoodItemCreate, FoodItemsResponse, ResultResponse,
    CookingStateResponse, DisplayState, DisplayStateResponse,
    DisplayStateRequest, DisplayContentRequest
)
from typing import Dict, Any
from logging_config import setup_logger

# 로거 설정
logger = setup_logger("refrigerator_service")

# 초기 냉장고 식재료 데이터
food_items = [
    FoodItem(name="소고기", quantity="200g"),
    FoodItem(name="사이다", quantity="1캔"),
    FoodItem(name="양파", quantity="3개"),
    FoodItem(name="생닭", quantity="4마리"),
    FoodItem(name="계란", quantity="10개"),
    FoodItem(name="소세지", quantity="4개"),
    FoodItem(name="치즈", quantity="3개"),
    FoodItem(name="호박", quantity="2개"),
    FoodItem(name="고구마", quantity="1개"),
    FoodItem(name="오징어", quantity="4마리"),
    FoodItem(name="고등어", quantity="1마리"),
    FoodItem(name="버섯", quantity="2개")
]

# 요리 상태 데이터
cooking_state = {}

# 디스플레이 상태 및 내용 데이터
display_state = DisplayState.OFF
display_content = ""

def get_food_items():
    """냉장고에 있는 식재료 리스트 조회"""
    logger.info("서비스 호출: 냉장고에 있는 식재료 리스트 조회")
    return FoodItemsResponse(items=food_items)

def add_food_item(food_item: FoodItemCreate):
    """냉장고에 식재료 추가"""
    logger.info(f"서비스 호출: 냉장고에 식재료 추가 ({food_item.name}, {food_item.quantity})")
    
    # 이미 있는 식재료인지 확인
    for existing_item in food_items:
        if existing_item.name == food_item.name:
            existing_item.quantity = food_item.quantity
            return ResultResponse(
                result="success", 
                message=f"식재료 '{food_item.name}'의 수량이 {food_item.quantity}(으)로 업데이트되었습니다."
            )
    
    # 새 식재료 추가
    new_item = FoodItem(name=food_item.name, quantity=food_item.quantity)
    food_items.append(new_item)
    
    return ResultResponse(
        result="success", 
        message=f"식재료 '{food_item.name}'이(가) {food_item.quantity} 추가되었습니다."
    )

def get_cooking_state():
    """냉장고 디스플레이 요리 상태 조회"""
    logger.info("서비스 호출: 냉장고 디스플레이 요리 상태 조회")
    return CookingStateResponse(state=cooking_state)

def set_cooking_state(step_info: Dict[str, Any]):
    """냉장고 디스플레이에 레시피 스텝 정보 설정"""
    logger.info(f"서비스 호출: 냉장고 디스플레이에 레시피 스텝 정보 설정")
    global cooking_state
    cooking_state = step_info
    return ResultResponse(
        result="success", 
        message="냉장고 디스플레이에 요리 상태가 업데이트되었습니다."
    )

def get_display_state():
    """냉장고 디스플레이 상태 조회"""
    logger.info("서비스 호출: 냉장고 디스플레이 상태 조회")
    return DisplayStateResponse(state=display_state)

def set_display_state(request: DisplayStateRequest):
    """냉장고 디스플레이 상태 설정"""
    logger.info(f"서비스 호출: 냉장고 디스플레이 상태 설정 ({request.state})")
    global display_state
    display_state = request.state
    
    # 디스플레이가 꺼지면 내용도 초기화
    if display_state == DisplayState.OFF:
        global display_content
        display_content = ""
    
    return ResultResponse(
        result="success", 
        message=f"냉장고 디스플레이 상태가 {request.state}로 설정되었습니다."
    )

def set_display_content(request: DisplayContentRequest):
    """냉장고 디스플레이 내용 설정"""
    logger.info(f"서비스 호출: 냉장고 디스플레이 내용 설정")
    global display_state, display_content
    
    if display_state == DisplayState.OFF:
        display_state = DisplayState.ON
        logger.info("디스플레이가 꺼져 있어 자동으로 켜집니다.")
    
    display_content = request.content
    
    return ResultResponse(
        result="success", 
        message="냉장고 디스플레이 내용이 설정되었습니다."
    ) 