from models.induction import PowerState, HeatLevel, ResultResponse, InductionState
from logging_config import setup_logger
from typing import Dict, Any

# 로거 설정
logger = setup_logger("induction_service")

# 화력 레벨 한글 표현 매핑
HEAT_LEVEL_KOREAN = {
    "HIGH": "강불",
    "MEDIUM": "중불",
    "LOW": "약불"
}

# 인덕션 상태 데이터
induction_state = {
    "power_state": PowerState.OFF,
    "is_cooking": False,
    "heat_level": None
}

def get_status() -> Dict[str, Any]:
    """인덕션 상태 조회"""
    logger.info("서비스 호출: 인덕션 상태 조회")
    
    response = {
        "power": induction_state["power_state"] == PowerState.ON,
        "cooking": induction_state["is_cooking"],
        "heat_level": induction_state["heat_level"]
    }
    
    # 상태 메시지 생성
    if induction_state["power_state"] == PowerState.ON:
        if induction_state["is_cooking"]:
            heat_level_korean = HEAT_LEVEL_KOREAN.get(induction_state['heat_level'], induction_state['heat_level'])
            response["message"] = f"인덕션이 {heat_level_korean}로 조리 중입니다."
        else:
            response["message"] = "인덕션 전원이 켜져 있습니다."
    else:
        response["message"] = "인덕션 전원이 꺼져 있습니다."
    
    return response

def toggle_power():
    """인덕션 전원 켜기/끄기"""
    global induction_state
    
    if induction_state["power_state"] == PowerState.OFF:
        induction_state["power_state"] = PowerState.ON
        logger.info("서비스 호출: 인덕션 전원 켜기")
        return ResultResponse(
            result="success",
            message="인덕션 전원이 켜졌습니다."
        )
    else:
        # 조리 중이면 먼저 중단
        if induction_state["is_cooking"]:
            stop_cooking()
            
        induction_state["power_state"] = PowerState.OFF
        logger.info("서비스 호출: 인덕션 전원 끄기")
        return ResultResponse(
            result="success",
            message="인덕션 전원이 꺼졌습니다."
        )

def start_cooking(heat_level: HeatLevel):
    """인덕션 조리 시작"""
    global induction_state
    
    if induction_state["power_state"] == PowerState.OFF:
        logger.warning("인덕션 전원이 꺼져 있어 조리를 시작할 수 없습니다.")
        return ResultResponse(
            result="error",
            message="인덕션 전원이 꺼져 있어 조리를 시작할 수 없습니다."
        )
    
    induction_state["is_cooking"] = True
    induction_state["heat_level"] = heat_level
    
    heat_level_korean = HEAT_LEVEL_KOREAN.get(heat_level, heat_level)
    logger.info(f"서비스 호출: 인덕션 조리 시작 (화력: {heat_level}, 한글: {heat_level_korean})")
    return ResultResponse(
        result="success",
        message=f"인덕션 조리가 {heat_level_korean}으로 시작되었습니다."
    )

def stop_cooking():
    """인덕션 조리 중단"""
    global induction_state
    
    if not induction_state["is_cooking"]:
        logger.warning("인덕션이 조리 중이 아닙니다.")
        return ResultResponse(
            result="error",
            message="인덕션이 조리 중이 아닙니다."
        )
    
    induction_state["is_cooking"] = False
    induction_state["heat_level"] = None
    
    logger.info("서비스 호출: 인덕션 조리 중단")
    return ResultResponse(
        result="success",
        message="인덕션 조리가 중단되었습니다."
    ) 