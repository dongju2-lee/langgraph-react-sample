from fastapi import APIRouter, HTTPException
from models.curtain_models import (
    CurtainPowerRequest, CurtainPositionRequest, CurtainScheduleRequest, CurtainResultResponse
)
from services.curtain_service import curtain_service
from logging_config import setup_logger
from typing import Dict, Any

# 로거 설정
logger = setup_logger("curtain_api")

router = APIRouter(prefix="/curtain", tags=["Curtain"], responses={404: {"description": "Not found"}})

@router.get("/status", response_model=Dict[str, Any])
async def get_status():
    """
    커튼 상태 조회
    
    - 요청 본문이 필요 없습니다.
    - 예시 요청: GET /curtain/status
    - 현재 커튼의 열림/닫힘 상태, 열림 비율, 스케줄 등 전반적인 상태 정보를 조회합니다.
    - 응답에는 power_state(열림/닫힘), position(열림 비율), schedules(예약된 스케줄 목록) 정보가 포함됩니다.
    """
    logger.info("API 호출: 커튼 상태 조회")
    try:
        return curtain_service.get_status()
    except Exception as e:
        logger.exception("커튼 상태 조회 실패")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/power", response_model=CurtainResultResponse)
async def set_power(req: CurtainPowerRequest):
    """
    커튼/블라인드 열기/닫기

    - power_state: "open" 또는 "close" (문자열)
    - 예시: { "power_state": "open" }
    - 커튼을 완전히 열거나 닫습니다.
    """
    logger.info(f"API 호출: 커튼 전원 {req.power_state}")
    try:
        return curtain_service.set_power(req)
    except Exception as e:
        logger.exception("커튼 전원 제어 실패")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/position", response_model=CurtainResultResponse)
async def set_position(req: CurtainPositionRequest):
    """
    커튼 부분 열기

    - percent: 커튼을 열 비율 (0~100 사이의 정수)
    - 예시: { "percent": 50 }
    - 0은 완전히 닫힘, 100은 완전히 열림을 의미합니다.
    - 커튼을 지정한 비율(%)만큼 열거나 닫습니다.
    """
    logger.info(f"API 호출: 커튼 위치 {req.percent}%")
    try:
        return curtain_service.set_position(req)
    except Exception as e:
        logger.exception("커튼 위치 제어 실패")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/schedule", response_model=CurtainResultResponse)
async def set_schedule(req: CurtainScheduleRequest):
    """
    커튼 스케줄 설정

    - time: 예약 시간 (예: "08:00", "18:30")
    - action: 동작 ("open" 또는 "close")
    - 예시: { "time": "08:00", "action": "open" }
    - 지정한 시간에 커튼을 자동으로 열거나 닫도록 예약합니다.
    """
    logger.info(f"API 호출: 커튼 스케줄 {req.time} {req.action}")
    try:
        return curtain_service.set_schedule(req)
    except Exception as e:
        logger.exception("커튼 스케줄 설정 실패")
        raise HTTPException(status_code=500, detail=str(e)) 