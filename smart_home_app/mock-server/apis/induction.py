from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any
from models.induction import HeatLevel
from services import induction_service
from logging_config import setup_logger
from pydantic import BaseModel

# 로거 설정
logger = setup_logger("induction_api")

# 요청 모델 정의
class InductionStartRequest(BaseModel):
    heat_level: HeatLevel

router = APIRouter(
    prefix="/api/induction",
    tags=["induction"],
    responses={404: {"description": "페이지를 찾을 수 없습니다."}},
)

# 인덕션 상태 관리
induction_state = {
    "power": False,  # False: 꺼짐, True: 켜짐
    "cooking": False,  # 조리 중인지 여부
    "heat_level": None  # 조리 화력
}

@router.get("/status", response_model=Dict[str, Any])
async def get_status():
    """
    인덕션 상태를 조회합니다.
    
    - 요청 본문이 필요 없습니다.
    - 예시 요청: GET /api/induction/status
    - 현재 인덕션의 전원 상태, 조리 중 여부, 화력 단계를 조회합니다.
    """
    logger.info("API 호출: 인덕션 상태 조회")
    return induction_service.get_status()

@router.post("/power", response_model=Dict[str, Any])
async def toggle_power():
    """
    인덕션 전원을 켜거나 끕니다.
    
    - 요청 본문이 필요 없습니다.
    - 예시 요청: {}
    - 현재 전원 상태가 꺼져 있으면 켜고, 켜져 있으면 끕니다.
    - 전원이 꺼지면 조리도 자동으로 중단됩니다.
    """
    logger.info("API 호출: 인덕션 전원 토글")
    
    result = induction_service.toggle_power()
    
    return {
        "result": result.result,
        "power": induction_service.get_status()["power"],
        "message": result.message
    }

@router.post("/start-cooking", response_model=Dict[str, Any])
async def start_cooking(request: InductionStartRequest):
    """
    인덕션 조리를 시작합니다.
    
    - heat_level: 화력 단계 (HIGH, MEDIUM, LOW 중 하나)
    - 예시 요청: { "heat_level": "MEDIUM" }
    - 지정한 화력으로 인덕션 조리를 시작합니다.
    - 전원이 꺼져 있으면 오류가 발생합니다.
    - 화력 단계 값: "HIGH" (강불), "MEDIUM" (중불), "LOW" (약불)
    """
    logger.info(f"API 호출: 인덕션 조리 시작 (화력: {request.heat_level})")
    
    result = induction_service.start_cooking(request.heat_level)
    
    if result.result == "error":
        raise HTTPException(status_code=400, detail=result.message)
    
    state = induction_service.get_status()
    
    return {
        "result": result.result,
        "cooking": state["cooking"],
        "heat_level": state["heat_level"],
        "message": result.message
    }

@router.post("/stop-cooking", response_model=Dict[str, Any])
async def stop_cooking():
    """
    인덕션 조리를 중단합니다.
    
    - 요청 본문이 필요 없습니다.
    - 예시 요청: {}
    - 현재 진행 중인 조리를 중단합니다.
    - 이미 조리 중이 아닌 경우에도 요청은 처리됩니다.
    """
    logger.info("API 호출: 인덕션 조리 중단")
    
    result = induction_service.stop_cooking()
    state = induction_service.get_status()
    
    return {
        "result": result.result,
        "cooking": state["cooking"],
        "message": result.message
    }