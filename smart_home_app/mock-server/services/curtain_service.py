from models.curtain_models import (
    CurtainPowerRequest, CurtainPositionRequest, CurtainScheduleRequest, CurtainResultResponse
)
from logging_config import setup_logger

logger = setup_logger("curtain_service")

class CurtainService:
    def set_power(self, req: CurtainPowerRequest) -> CurtainResultResponse:
        logger.info(f"커튼 전원 제어: {req.power_state}")
        return CurtainResultResponse(result="success", message=f"커튼이 {req.power_state} 상태로 변경됨")

    def set_position(self, req: CurtainPositionRequest) -> CurtainResultResponse:
        logger.info(f"커튼 위치 제어: {req.percent}%")
        return CurtainResultResponse(result="success", message=f"커튼이 {req.percent}% 위치로 이동됨")

    def set_schedule(self, req: CurtainScheduleRequest) -> CurtainResultResponse:
        logger.info(f"커튼 스케줄 설정: {req.time} {req.action}")
        return CurtainResultResponse(result="success", message=f"커튼이 {req.time}에 {req.action}으로 예약됨")

curtain_service = CurtainService() 