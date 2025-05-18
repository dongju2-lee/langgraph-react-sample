from models.light_models import (
    LightPowerRequest, LightBrightnessRequest, LightColorRequest, LightModeRequest, LightResultResponse
)
from logging_config import setup_logger

logger = setup_logger("light_service")

class LightService:
    def set_power(self, req: LightPowerRequest) -> LightResultResponse:
        logger.info(f"조명 전원 제어: {req.power_state}")
        return LightResultResponse(result="success", message=f"조명 전원이 {req.power_state} 상태로 변경됨")

    def set_brightness(self, req: LightBrightnessRequest) -> LightResultResponse:
        logger.info(f"조명 밝기 조절: {req.level}")
        return LightResultResponse(result="success", message=f"조명 밝기가 {req.level}으로 변경됨")

    def set_color(self, req: LightColorRequest) -> LightResultResponse:
        logger.info(f"조명 색상 변경: {req.color}")
        return LightResultResponse(result="success", message=f"조명 색상이 {req.color}로 변경됨")

    def set_mode(self, req: LightModeRequest) -> LightResultResponse:
        logger.info(f"조명 모드 적용: {req.mode}")
        return LightResultResponse(result="success", message=f"조명 모드가 {req.mode}로 변경됨")

light_service = LightService() 