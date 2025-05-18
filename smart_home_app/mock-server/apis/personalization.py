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
    """
    사용자의 개인 선호도 리스트 조회
    
    - 요청 본문이 필요 없습니다.
    - 예시 요청: GET /personalization/preferences
    - 사용자의 저장된 모든 개인 선호도 목록을 반환합니다.
    - 각 선호도는 ID, 카테고리, 설명을 포함합니다.
    """
    logger.info("API 호출: 사용자의 개인 선호도 리스트 조회")
    return personalization_service.get_preferences()

@router.post("/preferences", response_model=ResultResponse)
async def add_preference(preference: PreferenceCreate):
    """
    사용자의 개인 선호도 추가
    
    - category: 선호도 카테고리 (예: "식재료", "조리법", "음식 종류")
    - description: 선호도 세부 설명 (예: "매운 음식 선호", "채식 요리 선호")
    - 예시: { "category": "식재료", "description": "매운 음식 선호" }
    - 새로운 개인 선호도를 시스템에 추가합니다.
    """
    logger.info(f"API 호출: 사용자의 개인 선호도 추가 ({preference.description})")
    return personalization_service.add_preference(preference)

@router.delete("/preferences/{preference_id}", response_model=ResultResponse)
async def delete_preference(preference_id: int):
    """
    사용자의 개인 선호도 삭제
    
    - preference_id: 삭제할 선호도의 ID (정수)
    - 예시 요청: DELETE /personalization/preferences/1
    - 지정한 ID의 선호도를 시스템에서 삭제합니다.
    - 존재하지 않는 ID인 경우 에러를 반환합니다.
    """
    logger.info(f"API 호출: 사용자의 개인 선호도 삭제 (ID: {preference_id})")
    return personalization_service.delete_preference(preference_id)

@router.get("/appliances", response_model=ApplianceResponse)
async def get_appliances():
    """
    사용자가 보유한 주방 가전기기 목록 조회
    
    - 요청 본문이 필요 없습니다.
    - 예시 요청: GET /personalization/appliances
    - 사용자가 가지고 있는 모든 주방 가전기기 목록을 반환합니다.
    - 냉장고, 전자레인지, 인덕션 등의 정보를 포함합니다.
    """
    logger.info("API 호출: 사용자가 보유한 주방 가전기기 목록 조회")
    return personalization_service.get_appliances() 