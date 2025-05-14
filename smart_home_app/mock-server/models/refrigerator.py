from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Union
from enum import Enum

class FoodItem(BaseModel):
    """식재료 아이템 모델"""
    name: str
    quantity: str

class FoodItemCreate(BaseModel):
    """식재료 추가 요청 모델"""
    name: str
    quantity: str

class FoodItemsResponse(BaseModel):
    """식재료 목록 응답 모델"""
    items: List[FoodItem]

class DisplayState(str, Enum):
    """냉장고 디스플레이 상태 열거형"""
    ON = "디스플레이중"
    OFF = "디스플레이중아님"

class DisplayStateResponse(BaseModel):
    """냉장고 디스플레이 상태 응답 모델"""
    state: DisplayState

class DisplayStateRequest(BaseModel):
    """냉장고 디스플레이 상태 변경 요청 모델"""
    state: DisplayState

class DisplayContentRequest(BaseModel):
    """냉장고 디스플레이 내용 설정 요청 모델"""
    content: str

class ResultResponse(BaseModel):
    """결과 응답 모델"""
    result: str
    message: Optional[str] = None

class StepInfoRequest(BaseModel):
    """레시피 스텝 정보 요청 모델"""
    step_info: Dict[str, Any]

class CookingStateResponse(BaseModel):
    """요리 상태 응답 모델"""
    state: Dict[str, Any] 