from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any
import time
from logging_config import setup_logger

# 로거 설정
logger = setup_logger("microwave_api")

router = APIRouter(
    prefix="/api/microwave",
    tags=["microwave"],
    responses={404: {"description": "페이지를 찾을 수 없습니다."}},
)

# 전자레인지 상태 관리
microwave_state = {
    "power": False,  # False: 꺼짐, True: 켜짐
    "cooking": False,  # 조리 중인지 여부
    "start_time": None,  # 조리 시작 시간
    "duration": 0,  # 설정된 조리 시간 (초)
}

@router.post("/power", response_model=Dict[str, Any])
async def toggle_power():
    """
    전자레인지 전원을 켜거나 끕니다.
    
    - 요청 본문이 필요 없습니다.
    - 예시 요청: {}
    - 현재 전원 상태가 꺼져 있으면 켜고, 켜져 있으면 끕니다.
    - 전원이 꺼지면 조리도 자동으로 중단됩니다.
    """
    logger.info("API 호출: 전자레인지 전원 토글")
    
    microwave_state["power"] = not microwave_state["power"]
    
    # 전원이 꺼지면 조리도 중단
    if not microwave_state["power"]:
        microwave_state["cooking"] = False
        microwave_state["start_time"] = None
        microwave_state["duration"] = 0
    
    return {
        "result": "success",
        "power": microwave_state["power"],
        "message": f"전자레인지 전원이 {'켜졌습니다' if microwave_state['power'] else '꺼졌습니다'}"
    }

@router.post("/start", response_model=Dict[str, Any])
async def start_cooking(seconds: int = Body(...)):
    """
    전자레인지 조리를 시작합니다.
    
    - seconds: 조리 시간 (초 단위, 1 이상의 정수)
    - 예시 요청: { "seconds": 60 }
    - 지정한 시간(초) 동안 전자레인지 조리를 시작합니다.
    - 전원이 꺼져 있으면 오류가 발생합니다.
    - 조리 시간은 0보다 커야 합니다.
    """
    logger.info(f"API 호출: 전자레인지 조리 시작 (시간: {seconds}초)")
    
    if not microwave_state["power"]:
        raise HTTPException(status_code=400, detail="전자레인지 전원이 꺼져 있습니다. 먼저 전원을 켜주세요.")
    
    if seconds <= 0:
        raise HTTPException(status_code=400, detail="조리 시간은 0보다 커야 합니다.")
    
    microwave_state["cooking"] = True
    microwave_state["start_time"] = time.time()
    microwave_state["duration"] = seconds
    
    return {
        "result": "success",
        "cooking": True,
        "duration": seconds,
        "message": f"전자레인지 조리가 {seconds}초 동안 시작되었습니다."
    }

@router.get("/status", response_model=Dict[str, Any])
async def get_status():
    """
    전자레인지 조리 상태를 조회합니다.
    
    - 요청 본문이 필요 없습니다.
    - 예시 요청: GET /api/microwave/status
    - 현재 전자레인지의 전원 상태, 조리 중 여부를 조회합니다.
    - 조리 중인 경우 남은 시간(초)도 함께 반환합니다.
    """
    logger.info("API 호출: 전자레인지 조리 상태 조회")
    
    response = {
        "power": microwave_state["power"],
        "cooking": microwave_state["cooking"]
    }
    
    # 전원이 꺼져있는 경우
    if not microwave_state["power"]:
        response["message"] = "전자레인지 전원이 꺼져 있습니다."
        return response
    
    # 조리 중인 경우 남은 시간 계산
    if microwave_state["cooking"] and microwave_state["start_time"]:
        elapsed = time.time() - microwave_state["start_time"]
        remaining = max(0, microwave_state["duration"] - elapsed)
        
        # 조리 완료 확인
        if remaining <= 0:
            microwave_state["cooking"] = False
            microwave_state["start_time"] = None
            response["cooking"] = False
            response["remaining_seconds"] = 0
            response["message"] = "조리가 완료되었습니다."
        else:
            response["remaining_seconds"] = int(remaining)
            response["message"] = f"조리 중: 남은 시간 {int(remaining)}초"
    else:
        response["message"] = "전원이 켜져 있으나 조리 중이 아닙니다."
    
    return response

@router.post("/stop", response_model=Dict[str, Any])
async def stop_cooking():
    """
    전자레인지 조리를 중단합니다.
    
    - 요청 본문이 필요 없습니다.
    - 예시 요청: {}
    - 현재 진행 중인 조리를 중단합니다.
    - 이미 조리 중이 아닌 경우에도 요청은 성공하지만 결과는 "info"입니다.
    """
    logger.info("API 호출: 전자레인지 조리 중단")
    
    if not microwave_state["cooking"]:
        return {
            "result": "info",
            "cooking": False,
            "message": "전자레인지가 이미 조리 중이 아닙니다."
        }
    
    microwave_state["cooking"] = False
    microwave_state["start_time"] = None
    microwave_state["duration"] = 0
    
    return {
        "result": "success",
        "cooking": False,
        "message": "전자레인지 조리가 중단되었습니다."
    } 