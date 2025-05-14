from fastapi import APIRouter, HTTPException
from models.mobile import (
    Message, MessageCreate, MessageDelete,
    Calendar, CalendarCreate, CalendarDelete,
    MessageResponse, CalendarResponse, ResultResponse
)
from services import mobile_service
from logging_config import setup_logger

# 로거 설정
logger = setup_logger("mobile_api")

router = APIRouter(
    prefix="/mobile",
    tags=["Mobile"],
    responses={404: {"description": "Not found"}},
)

@router.get("/messages", response_model=list[Message])
async def get_messages():
    """보낸 문자 메시지 목록 조회"""
    logger.info("API 호출: 보낸 문자 메시지 목록 조회")
    return mobile_service.get_messages()

@router.post("/messages", response_model=ResultResponse)
async def send_message(message: MessageCreate):
    """문자 메시지 보내기"""
    logger.info(f"API 호출: 문자 메시지 보내기 (제목: {message.title}, 받는사람: {message.recipient})")
    return mobile_service.send_message(message)

@router.delete("/messages/{message_id}", response_model=ResultResponse)
async def delete_message(message_id: int):
    """문자 메시지 삭제"""
    logger.info(f"API 호출: 문자 메시지 삭제 (ID: {message_id})")
    return mobile_service.delete_message(message_id)

@router.get("/calendar", response_model=list[Calendar])
async def get_calendar_events():
    """캘린더 일정 목록 조회"""
    logger.info("API 호출: 캘린더 일정 목록 조회")
    return mobile_service.get_calendar_events()

@router.post("/calendar", response_model=ResultResponse)
async def add_calendar_event(event: CalendarCreate):
    """캘린더 일정 추가"""
    logger.info(f"API 호출: 캘린더 일정 추가 (제목: {event.title}, 날짜: {event.date})")
    return mobile_service.add_calendar_event(event)

@router.delete("/calendar/{event_id}", response_model=ResultResponse)
async def delete_calendar_event(event_id: int):
    """캘린더 일정 삭제"""
    logger.info(f"API 호출: 캘린더 일정 삭제 (ID: {event_id})")
    return mobile_service.delete_calendar_event(event_id) 