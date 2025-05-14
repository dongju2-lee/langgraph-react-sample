from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel
import uuid
from datetime import datetime

class Message(BaseModel):
    """문자 메시지 모델"""
    id: int
    title: str
    content: str
    time: datetime
    recipient: str

class MessageCreate(BaseModel):
    """문자 메시지 생성 요청 모델"""
    title: str
    content: str
    time: Optional[datetime] = None
    recipient: str

class MessageDelete(BaseModel):
    """문자 메시지 삭제 요청 모델"""
    id: int

class Calendar(BaseModel):
    """캘린더 일정 모델"""
    id: int
    date: datetime
    title: str
    content: str

class CalendarCreate(BaseModel):
    """캘린더 일정 생성 요청 모델"""
    date: datetime
    title: str
    content: str

class CalendarDelete(BaseModel):
    """캘린더 일정 삭제 요청 모델"""
    id: int

class MessageResponse(BaseModel):
    """문자 메시지 목록 응답 모델"""
    messages: List[Message]

class CalendarResponse(BaseModel):
    """캘린더 일정 목록 응답 모델"""
    events: List[Calendar]

class ResultResponse(BaseModel):
    """결과 응답 모델"""
    result: str
    message: Optional[str] = None
    id: Optional[str] = None