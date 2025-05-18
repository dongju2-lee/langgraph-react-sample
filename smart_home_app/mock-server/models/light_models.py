from pydantic import BaseModel

class LightPowerRequest(BaseModel):
    power_state: str  # "on" | "off"

class LightBrightnessRequest(BaseModel):
    level: int

class LightColorRequest(BaseModel):
    color: str  # "warm" | "cool" | "blue" 등

class LightModeRequest(BaseModel):
    mode: str  # "study" | "relax" | "healing"

class LightResultResponse(BaseModel):
    result: str
    message: str 