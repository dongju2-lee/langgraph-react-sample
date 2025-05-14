from fastapi import APIRouter, HTTPException
from models.personalization import (
    Preference, PreferenceCreate, PreferenceDelete,
    ApplianceResponse, ResultResponse
)
from services import personalization_service
from logging_config import setup_logger

# 로거 설정
logger = setup_logger("personalization_api")

router = APIRouter(
    prefix="/personalization",
    tags=["Personalization"],
    responses={404: {"description": "Not found"}},
)

@router.get("/preferences", response_model=list[Preference])
async def get_preferences():
    """사용자의 개인 선호도 리스트 조회"""
    logger.info("API 호출: 사용자의 개인 선호도 리스트 조회")
    return personalization_service.get_preferences()

@router.post("/preferences", response_model=ResultResponse)
async def add_preference(preference: PreferenceCreate):
    """사용자의 개인 선호도 추가"""
    logger.info(f"API 호출: 사용자의 개인 선호도 추가 ({preference.description})")
    return personalization_service.add_preference(preference)

@router.delete("/preferences/{preference_id}", response_model=ResultResponse)
async def delete_preference(preference_id: int):
    """사용자의 개인 선호도 삭제"""
    logger.info(f"API 호출: 사용자의 개인 선호도 삭제 (ID: {preference_id})")
    return personalization_service.delete_preference(preference_id)

@router.get("/appliances", response_model=ApplianceResponse)
async def get_appliances():
    """사용자가 보유한 주방 가전기기 목록 조회"""
    logger.info("API 호출: 사용자가 보유한 주방 가전기기 목록 조회")
    return personalization_service.get_appliances() 