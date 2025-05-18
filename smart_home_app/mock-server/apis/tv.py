from fastapi import APIRouter, HTTPException
from models.tv_models import (
    TVPowerRequest, TVChannelRequest, TVVolumeRequest, 
    TVResultResponse, TVChannelsResponse
)
from services.tv_service import tv_service
from logging_config import setup_logger
from typing import Dict, Any

# 로거 설정
logger = setup_logger("tv_api")

router = APIRouter(prefix="/tv", tags=["TV"], responses={404: {"description": "Not found"}})

@router.get("/status", response_model=Dict[str, Any])
async def get_status():
    """
    TV 상태 조회
    
    - 요청 본문이 필요 없습니다.
    - 예시 요청: GET /tv/status
    - 현재 TV의 전원 상태, 채널, 볼륨 등 전반적인 상태 정보를 조회합니다.
    - 응답에는 power(전원), current_channel(현재 채널), volume(볼륨) 정보가 포함됩니다.
    """
    logger.info("API 호출: TV 상태 조회")
    try:
        return tv_service.get_status()
    except Exception as e:
        logger.exception("TV 상태 조회 실패")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/power", response_model=TVResultResponse)
async def set_power(req: TVPowerRequest):
    """
    TV 전원 ON/OFF

    - power_state: "on" 또는 "off" (문자열)
    - 예시: { "power_state": "on" }
    - TV의 전원을 켜거나 끕니다.
    """
    logger.info(f"API 호출: TV 전원 {req.power_state}")
    try:
        return tv_service.set_power(req)
    except Exception as e:
        logger.exception("TV 전원 제어 실패")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/channel", response_model=TVResultResponse)
async def set_channel(req: TVChannelRequest):
    """
    TV 채널 변경

    - channel: 변경할 채널명 (예: "EBC", "MBB", "너튜브" 등)
    - 예시: { "channel": "EBC" }
    - TV의 채널을 지정한 채널로 변경합니다.
    """
    logger.info(f"API 호출: TV 채널 변경 {req.channel}")
    try:
        return tv_service.set_channel(req)
    except Exception as e:
        logger.exception("TV 채널 변경 실패")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/volume", response_model=TVResultResponse)
async def set_volume(req: TVVolumeRequest):
    """
    TV 볼륨 조절

    - level: 볼륨 값 (0~100 사이의 정수, 예: 10)
    - 예시: { "level": 10 }
    - TV의 볼륨을 지정한 값으로 설정합니다.
    """
    logger.info(f"API 호출: TV 볼륨 {req.level}")
    try:
        return tv_service.set_volume(req)
    except Exception as e:
        logger.exception("TV 볼륨 조절 실패")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/channels", response_model=TVChannelsResponse)
async def get_channels():
    """
    TV 채널 목록 조회
    
    - 요청 본문이 필요 없습니다.
    - 예시 요청: GET /tv/channels
    - 현재 시청 가능한 모든 TV 채널 목록을 반환합니다.
    - 각 채널은 이름, 설명, 카테고리 정보를 포함합니다.
    - 제공 채널: MBB(예능), EBC(교육), 너튜브(영상/스포츠) 등
    """
    logger.info("API 호출: TV 채널 목록 조회")
    try:
        return tv_service.get_channels()
    except Exception as e:
        logger.exception("TV 채널 목록 조회 실패")
        raise HTTPException(status_code=500, detail=str(e)) 