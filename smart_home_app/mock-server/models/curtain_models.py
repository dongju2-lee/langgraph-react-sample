from pydantic import BaseModel

class CurtainPowerRequest(BaseModel):
    power_state: str  # "open" | "close"

class CurtainPositionRequest(BaseModel):
    percent: int  # 0~100

class CurtainScheduleRequest(BaseModel):
    time: str  # "08:00" 등
    action: str  # "open" | "close"

class CurtainResultResponse(BaseModel):
    result: str
    message: str 