from fastapi import APIRouter, HTTPException
from models.light_models import (
    LightPowerRequest, LightBrightnessRequest, LightColorRequest, LightModeRequest, LightResultResponse
)
from services.light_service import light_service
from logging_config import setup_logger
from typing import Dict, Any

# 로거 설정
logger = setup_logger("light_api")

router = APIRouter(prefix="/light", tags=["Light"], responses={404: {"description": "Not found"}})

@router.get("/status", response_model=Dict[str, Any])
async def get_status():
    """
    조명 상태 조회
    
    - 요청 본문이 필요 없습니다.
    - 예시 요청: GET /light/status
    - 현재 조명의 전원 상태, 밝기, 색상, 모드 등 전반적인 상태 정보를 조회합니다.
    - 응답에는 power(전원), brightness(밝기), color(색상), mode(모드) 정보가 포함됩니다.
    """
    logger.info("API 호출: 조명 상태 조회")
    try:
        return light_service.get_status()
    except Exception as e:
        logger.exception("조명 상태 조회 실패")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/power", response_model=LightResultResponse)
async def set_power(req: LightPowerRequest):
    """
    조명 전원 ON/OFF

    - power_state: "on" 또는 "off" (문자열)
    - 예시: { "power_state": "on" }
    - 조명의 전원을 켜거나 끕니다.
    """
    logger.info(f"API 호출: 조명 전원 {req.power_state}")
    try:
        return light_service.set_power(req)
    except Exception as e:
        logger.exception("조명 전원 제어 실패")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/brightness", response_model=LightResultResponse)
async def set_brightness(req: LightBrightnessRequest):
    """
    조명 밝기 조절

    - level: 밝기 값 (0~100 사이의 정수, 예: 80)
    - 예시: { "level": 80 }
    - 조명의 밝기를 지정한 값으로 설정합니다.
    """
    logger.info(f"API 호출: 조명 밝기 {req.level}")
    try:
        return light_service.set_brightness(req)
    except Exception as e:
        logger.exception("조명 밝기 조절 실패")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/color", response_model=LightResultResponse)
async def set_color(req: LightColorRequest):
    """
    조명 색상 변경

    - color: 색상명 (예: "warm", "cool", "blue")
    - 예시: { "color": "warm" }
    - 조명의 색상을 지정한 값으로 변경합니다.
    """
    logger.info(f"API 호출: 조명 색상 {req.color}")
    try:
        return light_service.set_color(req)
    except Exception as e:
        logger.exception("조명 색상 변경 실패")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/mode", response_model=LightResultResponse)
async def set_mode(req: LightModeRequest):
    """
    조명 프리셋 모드 적용

    - mode: 프리셋 모드명 (예: "study", "relax", "healing")
    - 예시: { "mode": "study" }
    - 조명에 미리 정의된 프리셋 모드를 적용합니다.
    """
    logger.info(f"API 호출: 조명 모드 {req.mode}")
    try:
        return light_service.set_mode(req)
    except Exception as e:
        logger.exception("조명 모드 적용 실패")
        raise HTTPException(status_code=500, detail=str(e)) 