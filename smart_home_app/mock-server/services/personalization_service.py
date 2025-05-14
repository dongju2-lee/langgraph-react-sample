from models.personalization import Preference, PreferenceCreate, ApplianceResponse, ResultResponse
from logging_config import setup_logger

# 로거 설정
logger = setup_logger("personalization_service")

# 초기 개인 선호도 데이터
preferences = [
    Preference(id=1, description="소고기를 좋아함"),
    Preference(id=2, description="돼지고기도 좋아함"),
    Preference(id=3, description="오이는 정말 싫어함"),
    Preference(id=4, description="야채를 잘 먹지 않음"),
    Preference(id=5, description="매운음식은 잘먹지 않음"),
    Preference(id=6, description="여동생이 있음"),
    Preference(id=7, description="주로 저녁을 집에서 먹음"),
    Preference(id=8, description="튀긴음식을 좋아함"),
    Preference(id=9, description="피자를 좋아함")
]

# 가전기기 데이터
appliances = ["인덕션", "전자레인지", "냉장고"]

def get_preferences():
    """사용자의 개인 선호도 리스트 조회"""
    logger.info("서비스 호출: 사용자의 개인 선호도 리스트 조회")
    return preferences

def add_preference(preference: PreferenceCreate):
    """사용자의 개인 선호도 추가"""
    logger.info(f"서비스 호출: 사용자의 개인 선호도 추가 ({preference.description})")
    # 새 ID 생성 (기존 ID 중 가장 큰 값 + 1)
    new_id = max([p.id for p in preferences]) + 1 if preferences else 1
    new_preference = Preference(id=new_id, description=preference.description)
    preferences.append(new_preference)
    return ResultResponse(
        result="success",
        message=f"선호도 '{preference.description}'이(가) 추가되었습니다."
    )

def delete_preference(preference_id: int):
    """사용자의 개인 선호도 삭제"""
    logger.info(f"서비스 호출: 사용자의 개인 선호도 삭제 (ID: {preference_id})")
    for i, pref in enumerate(preferences):
        if pref.id == preference_id:
            removed = preferences.pop(i)
            return ResultResponse(
                result="success",
                message=f"선호도 '{removed.description}'이(가) 삭제되었습니다."
            )
    return ResultResponse(
        result="error",
        message=f"ID가 {preference_id}인 선호도를 찾을 수 없습니다."
    )

def get_appliances():
    """사용자가 보유한 주방 가전기기 목록 조회"""
    logger.info("서비스 호출: 사용자가 보유한 주방 가전기기 목록 조회")
    return ApplianceResponse(appliances=appliances) 