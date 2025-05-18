from models.curtain_models import (
    CurtainPowerRequest, CurtainPositionRequest, CurtainScheduleRequest, CurtainResultResponse
)
from logging_config import setup_logger
from typing import Dict, Any, List

logger = setup_logger("curtain_service")

# 커튼 상태 저장용 전역 변수
curtain_state = {
    "power_state": "close",  # "open" 또는 "close"
    "position": 0,  # 열림 비율 (0-100%)
    "schedules": []  # 등록된 스케줄 목록
}

class CurtainService:
    def get_status(self) -> Dict[str, Any]:
        """
        커튼 상태 정보 조회
        """
        logger.info("커튼 상태 조회")
        
        # 스케줄 정보 형태 가공
        schedule_info = []
        for schedule in curtain_state["schedules"]:
            schedule_info.append({
                "time": schedule["time"],
                "action": schedule["action"]
            })
        
        return {
            "power_state": curtain_state["power_state"],
            "position": curtain_state["position"],
            "is_open": curtain_state["power_state"] == "open" or curtain_state["position"] > 0,
            "schedules": schedule_info,
            "message": (
                f"커튼이 {curtain_state['position']}% 열려 있습니다." 
                if curtain_state["position"] > 0 else (
                    "커튼이 완전히 열려 있습니다." if curtain_state["power_state"] == "open" 
                    else "커튼이 닫혀 있습니다."
                )
            )
        }
        
    def set_power(self, req: CurtainPowerRequest) -> CurtainResultResponse:
        logger.info(f"커튼 전원 제어: {req.power_state}")
        # 상태 업데이트
        curtain_state["power_state"] = req.power_state
        
        # 위치 정보도 동기화
        if req.power_state == "open":
            curtain_state["position"] = 100
        elif req.power_state == "close":
            curtain_state["position"] = 0
            
        return CurtainResultResponse(result="success", message=f"커튼이 {req.power_state} 상태로 변경됨")

    def set_position(self, req: CurtainPositionRequest) -> CurtainResultResponse:
        logger.info(f"커튼 위치 제어: {req.percent}%")
        # 위치 범위 확인
        if not (0 <= req.percent <= 100):
            logger.warning(f"유효하지 않은 위치 값: {req.percent}")
            return CurtainResultResponse(result="error", message="커튼 위치 값은 0에서 100 사이여야 합니다.")
        
        # 상태 업데이트
        curtain_state["position"] = req.percent
        
        # 전원 상태도 동기화
        if req.percent == 0:
            curtain_state["power_state"] = "close"
        elif req.percent == 100:
            curtain_state["power_state"] = "open"
        else:
            # 부분적으로 열린 경우 power_state는 변경하지 않음
            pass
            
        return CurtainResultResponse(result="success", message=f"커튼이 {req.percent}% 위치로 이동됨")

    def set_schedule(self, req: CurtainScheduleRequest) -> CurtainResultResponse:
        logger.info(f"커튼 스케줄 설정: {req.time} {req.action}")
        
        # 스케줄 추가
        new_schedule = {
            "time": req.time,
            "action": req.action
        }
        
        # 같은 시간의 기존 스케줄이 있으면 업데이트
        for i, schedule in enumerate(curtain_state["schedules"]):
            if schedule["time"] == req.time:
                curtain_state["schedules"][i] = new_schedule
                return CurtainResultResponse(result="success", message=f"커튼이 {req.time}에 {req.action}으로 예약 업데이트됨")
        
        # 새 스케줄 추가
        curtain_state["schedules"].append(new_schedule)
        return CurtainResultResponse(result="success", message=f"커튼이 {req.time}에 {req.action}으로 예약됨")

curtain_service = CurtainService() 