from pydantic import BaseModel
from typing import List

class TVPowerRequest(BaseModel):
    power_state: str  # "on" | "off"

class TVChannelRequest(BaseModel):
    channel: str

class TVVolumeRequest(BaseModel):
    level: int

class TVResultResponse(BaseModel):
    result: str
    message: str

class TVChannel(BaseModel):
    name: str
    description: str
    category: str

class TVChannelsResponse(BaseModel):
    channels: List[TVChannel] 