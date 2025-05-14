from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel
import uuid

class Preference(BaseModel):
    """사용자 선호도 모델"""
    id: int
    description: str

class PreferenceCreate(BaseModel):
    """선호도 생성 요청 모델"""
    description: str

class PreferenceDelete(BaseModel):
    """선호도 삭제 요청 모델"""
    id: int

class ApplianceResponse(BaseModel):
    """사용자 가전기기 응답 모델"""
    appliances: List[str]

class ResultResponse(BaseModel):
    """결과 응답 모델"""
    result: str
    message: Optional[str] = None

class KitchenAppliance(BaseModel):
    name: str
    available: bool = True

class UserPreferences(BaseModel):
    preferences: List[Preference] = []
    kitchen_appliances: List[KitchenAppliance] = [
        KitchenAppliance(name="인덕션"),
        KitchenAppliance(name="전자레인지"),
        KitchenAppliance(name="냉장고")
    ] 