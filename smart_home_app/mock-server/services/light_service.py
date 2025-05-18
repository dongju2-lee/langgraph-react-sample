from models.light_models import (
    LightPowerRequest, LightBrightnessRequest, LightColorRequest, LightModeRequest, LightResultResponse
)
from logging_config import setup_logger
from typing import Dict, Any

logger = setup_logger("light_service")

# 조명 상태 저장용 전역 변수
light_state = {
    "power_state": "off",  # "on" 또는 "off"
    "brightness": 50,  # 기본 밝기 (0-100)
    "color": "warm",  # 기본 색상
    "mode": "normal",  # 기본 모드
}

class LightService:
    def get_status(self) -> Dict[str, Any]:
        """
        조명 상태 정보 조회
        """
        logger.info("조명 상태 조회")
        
        return {
            "power": light_state["power_state"] == "on",
            "brightness": light_state["brightness"],
            "color": light_state["color"],
            "mode": light_state["mode"],
            "message": f"조명은 현재 {light_state['power_state']} 상태" + (
                f", 밝기 {light_state['brightness']}%, 색상 '{light_state['color']}', 모드 '{light_state['mode']}'입니다." 
                if light_state["power_state"] == "on" else "입니다."
            )
        }
    
    def set_power(self, req: LightPowerRequest) -> LightResultResponse:
        logger.info(f"조명 전원 제어: {req.power_state}")
        # 상태 업데이트
        light_state["power_state"] = req.power_state
        return LightResultResponse(result="success", message=f"조명 전원이 {req.power_state} 상태로 변경됨")

    def set_brightness(self, req: LightBrightnessRequest) -> LightResultResponse:
        logger.info(f"조명 밝기 조절: {req.level}")
        # 밝기 범위 확인
        if not (0 <= req.level <= 100):
            logger.warning(f"유효하지 않은 밝기 레벨: {req.level}")
            return LightResultResponse(result="error", message="밝기 레벨은 0에서 100 사이여야 합니다.")
            
        # 전원이 켜져 있는지 확인
        if light_state["power_state"] != "on":
            logger.warning("조명 전원이 꺼져 있어 밝기를 조절할 수 없습니다.")
            return LightResultResponse(result="error", message="조명 전원이 꺼져 있어 밝기를 조절할 수 없습니다.")
        
        # 상태 업데이트
        light_state["brightness"] = req.level
        return LightResultResponse(result="success", message=f"조명 밝기가 {req.level}으로 변경됨")

    def set_color(self, req: LightColorRequest) -> LightResultResponse:
        logger.info(f"조명 색상 변경: {req.color}")
        # 전원이 켜져 있는지 확인
        if light_state["power_state"] != "on":
            logger.warning("조명 전원이 꺼져 있어 색상을 변경할 수 없습니다.")
            return LightResultResponse(result="error", message="조명 전원이 꺼져 있어 색상을 변경할 수 없습니다.")
        
        # 상태 업데이트
        light_state["color"] = req.color
        return LightResultResponse(result="success", message=f"조명 색상이 {req.color}로 변경됨")

    def set_mode(self, req: LightModeRequest) -> LightResultResponse:
        logger.info(f"조명 모드 적용: {req.mode}")
        # 전원이 켜져 있는지 확인
        if light_state["power_state"] != "on":
            logger.warning("조명 전원이 꺼져 있어 모드를 변경할 수 없습니다.")
            return LightResultResponse(result="error", message="조명 전원이 꺼져 있어 모드를 변경할 수 없습니다.")
        
        # 상태 업데이트
        light_state["mode"] = req.mode
        return LightResultResponse(result="success", message=f"조명 모드가 {req.mode}로 변경됨")

light_service = LightService() 