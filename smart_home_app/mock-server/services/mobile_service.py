from models.mobile import (
    Message, MessageCreate, MessageDelete, Calendar, CalendarCreate, 
    CalendarDelete, ResultResponse
)
from datetime import datetime
from logging_config import setup_logger

# 로거 설정
logger = setup_logger("mobile_service")

# 초기 문자 메시지 데이터
messages = [
    Message(
        id=1,
        title="환영합니다!",
        content="스마트홈 앱을 설치해주셔서 감사합니다.",
        time=datetime.now(),
        recipient="사용자"
    ),
    Message(
        id=2,
        title="냉장고 식재료 알림",
        content="오늘 소고기 유통기한이 만료됩니다. 빨리 드세요!",
        time=datetime.now(),
        recipient="사용자"
    )
]

# 초기 캘린더 일정 데이터
calendar_events = [
    Calendar(
        id=1,
        date=datetime.now(),
        title="스마트홈 앱 설치",
        content="스마트홈 앱 설치 및 초기 설정 완료"
    ),
    Calendar(
        id=2,
        date=datetime.now(),
        title="냉장고 식재료 정리",
        content="유통기한 지난 식재료 정리하기"
    )
]

def get_messages():
    """보낸 문자 메시지 목록 조회"""
    logger.info("서비스 호출: 보낸 문자 메시지 목록 조회")
    return messages

def send_message(message: MessageCreate):
    """문자 메시지 보내기"""
    logger.info(f"서비스 호출: 문자 메시지 보내기 (제목: {message.title}, 받는사람: {message.recipient})")
    
    # 새 ID 생성 (기존 ID 중 가장 큰 값 + 1)
    new_id = max([msg.id for msg in messages]) + 1 if messages else 1
    
    # 새 메시지 생성
    new_message = Message(
        id=new_id,
        title=message.title,
        content=message.content,
        time=message.time if message.time else datetime.now(),
        recipient=message.recipient
    )
    
    messages.append(new_message)
    
    return ResultResponse(
        result="success",
        message="문자 메시지가 성공적으로 전송되었습니다.",
        id=str(new_id)
    )

def delete_message(message_id: int):
    """문자 메시지 삭제"""
    logger.info(f"서비스 호출: 문자 메시지 삭제 (ID: {message_id})")
    
    for i, msg in enumerate(messages):
        if msg.id == message_id:
            deleted_msg = messages.pop(i)
            return ResultResponse(
                result="success", 
                message=f"문자 메시지 '{deleted_msg.title}'이(가) 삭제되었습니다.",
                id=str(message_id)
            )
    
    return ResultResponse(
        result="error",
        message=f"ID가 {message_id}인 문자 메시지를 찾을 수 없습니다."
    )

def get_calendar_events():
    """캘린더 일정 목록 조회"""
    logger.info("서비스 호출: 캘린더 일정 목록 조회")
    return calendar_events

def add_calendar_event(event: CalendarCreate):
    """캘린더 일정 추가"""
    logger.info(f"서비스 호출: 캘린더 일정 추가 (제목: {event.title}, 날짜: {event.date})")
    
    # 새 ID 생성 (기존 ID 중 가장 큰 값 + 1)
    new_id = max([evt.id for evt in calendar_events]) + 1 if calendar_events else 1
    
    # 새 일정 생성
    new_event = Calendar(
        id=new_id,
        date=event.date,
        title=event.title,
        content=event.content
    )
    
    calendar_events.append(new_event)
    
    return ResultResponse(
        result="success",
        message="캘린더 일정이 성공적으로 추가되었습니다.",
        id=str(new_id)
    )

def delete_calendar_event(event_id: int):
    """캘린더 일정 삭제"""
    logger.info(f"서비스 호출: 캘린더 일정 삭제 (ID: {event_id})")
    
    for i, evt in enumerate(calendar_events):
        if evt.id == event_id:
            deleted_evt = calendar_events.pop(i)
            return ResultResponse(
                result="success", 
                message=f"캘린더 일정 '{deleted_evt.title}'이(가) 삭제되었습니다.",
                id=str(event_id)
            )
    
    return ResultResponse(
        result="error",
        message=f"ID가 {event_id}인 캘린더 일정을 찾을 수 없습니다."
    ) 