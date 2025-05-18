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
    """
    보낸 문자 메시지 목록 조회
    
    - 요청 본문이 필요 없습니다.
    - 예시 요청: GET /mobile/messages
    - 사용자가 보낸 모든 메시지 목록을 반환합니다.
    - 각 메시지는 ID, 제목, 내용, 수신자, 전송 시간을 포함합니다.
    """
    logger.info("API 호출: 보낸 문자 메시지 목록 조회")
    return mobile_service.get_messages()

@router.post("/messages", response_model=ResultResponse)
async def send_message(message: MessageCreate):
    """
    문자 메시지 보내기
    
    - title: 메시지 제목 (문자열)
    - content: 메시지 내용 (문자열)
    - recipient: 수신자 (문자열, 전화번호 또는 이름)
    - 예시: { "title": "알림", "content": "집중 시간입니다", "recipient": "나의 휴대폰" }
    - 지정한 수신자에게 문자 메시지를 전송합니다.
    """
    logger.info(f"API 호출: 문자 메시지 보내기 (제목: {message.title}, 받는사람: {message.recipient})")
    return mobile_service.send_message(message)

@router.delete("/messages/{message_id}", response_model=ResultResponse)
async def delete_message(message_id: int):
    """
    문자 메시지 삭제
    
    - message_id: 삭제할 메시지 ID (정수)
    - 예시 요청: DELETE /mobile/messages/1
    - 지정한 ID의 메시지를 삭제합니다.
    - 존재하지 않는 ID인 경우 에러를 반환합니다.
    """
    logger.info(f"API 호출: 문자 메시지 삭제 (ID: {message_id})")
    return mobile_service.delete_message(message_id)

@router.get("/calendar", response_model=list[Calendar])
async def get_calendar_events():
    """
    캘린더 일정 목록 조회
    
    - 요청 본문이 필요 없습니다.
    - 예시 요청: GET /mobile/calendar
    - 사용자의 모든 캘린더 일정 목록을 반환합니다.
    - 각 일정은 ID, 제목, 내용, 날짜, 시간 정보를 포함합니다.
    """
    logger.info("API 호출: 캘린더 일정 목록 조회")
    return mobile_service.get_calendar_events()

@router.post("/calendar", response_model=ResultResponse)
async def add_calendar_event(event: CalendarCreate):
    """
    캘린더 일정 추가
    
    - title: 일정 제목 (문자열)
    - content: 일정 내용 (문자열)
    - date: 날짜 (문자열, "YYYY-MM-DD" 형식)
    - time: 시간 (선택 사항, 문자열, "HH:MM" 형식)
    - 예시: { "title": "스터디 모임", "content": "수학 스터디", "date": "2023-12-15", "time": "14:00" }
    - 지정한 정보로 새 캘린더 일정을 추가합니다.
    """
    logger.info(f"API 호출: 캘린더 일정 추가 (제목: {event.title}, 날짜: {event.date})")
    return mobile_service.add_calendar_event(event)

@router.delete("/calendar/{event_id}", response_model=ResultResponse)
async def delete_calendar_event(event_id: int):
    """
    캘린더 일정 삭제
    
    - event_id: 삭제할 일정 ID (정수)
    - 예시 요청: DELETE /mobile/calendar/1
    - 지정한 ID의 캘린더 일정을 삭제합니다.
    - 존재하지 않는 ID인 경우 에러를 반환합니다.
    """
    logger.info(f"API 호출: 캘린더 일정 삭제 (ID: {event_id})")
    return mobile_service.delete_calendar_event(event_id) 