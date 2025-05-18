import json
import requests
import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# 환경 변수 로드
load_dotenv()
MOCK_SERVER_URL = os.environ.get("MOCK_SERVER_URL", "http://localhost:10000")
MOBILE_MCP_NAME = os.environ.get("MOBILE_MCP_NAME", "mobile")
MOBILE_MCP_HOST = os.environ.get("MOBILE_MCP_HOST", "0.0.0.0")
MOBILE_MCP_PORT = int(os.environ.get("MOBILE_MCP_PORT", 10004))
MOBILE_MCP_INSTRUCTIONS = os.environ.get("MOBILE_MCP_INSTRUCTIONS", "모바일 기능을 제어하는 도구입니다. 메시지 조회/전송/삭제, 캘린더 일정 조회/추가/삭제, 알람 설정 등의 기능을 제공합니다.")

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("mobile_mcp_server")

# FastMCP 인스턴스 생성
mcp = FastMCP(
    MOBILE_MCP_NAME,  # MCP 서버 이름
    instructions=MOBILE_MCP_INSTRUCTIONS,
    host=MOBILE_MCP_HOST,  # 모든 IP에서 접속 허용
    port=MOBILE_MCP_PORT,  # 포트 번호
)

# 모의 API 요청 함수
async def mock_api_request(path: str, method: str = "GET", data: Optional[Dict] = None) -> Dict:
    """실제 모의 서버에 API 요청을 보내는 함수"""
    url = f"{MOCK_SERVER_URL}{path}"
    logger.info(f"모의 서버 API 요청: {method} {url}")
    
    try:
        if method.upper() == "GET":
            response = requests.get(url)
        elif method.upper() == "POST":
            response = requests.post(url, json=data)
        elif method.upper() == "DELETE":
            response = requests.delete(url)
        else:
            return {"error": f"지원하지 않는 HTTP 메서드: {method}"}
        
        response.raise_for_status()
        result = response.json()
        logger.info(f"모의 서버 응답: {json.dumps(result, ensure_ascii=False)}")
        return result
    except Exception as e:
        logger.error(f"모의 서버 요청 실패: {str(e)}")
        return {"error": f"모의 서버 요청 실패: {str(e)}"}

@mcp.tool()
async def get_messages() -> Dict[str, Any]:
    """
    보낸 문자 메시지 목록을 조회합니다.
    사용자의 모든 메시지를 시간순으로 정렬하여 반환합니다.
    
    Args:
        없음
        
    Returns:
        Dict[str, Any]: 메시지 목록을 포함하는 딕셔너리
        
    예시 요청:
        get_messages()
        
    예시 응답:
        {
            "messages": [
                {
                    "id": 1,
                    "title": "집 전등 상태",
                    "content": "집 전등이 켜져 있습니다. 외출 중이신가요?",
                    "recipient": "홍길동",
                    "timestamp": "2023-04-15T14:30:00"
                },
                {
                    "id": 2,
                    "title": "냉장고 온도 알림",
                    "content": "냉장고 온도가 상승했습니다. 확인이 필요합니다.",
                    "recipient": "스마트홈 관리자",
                    "timestamp": "2023-04-16T09:15:00"
                }
            ],
            "count": 2,
            "message": "2개의 메시지가 있습니다."
        }
    """
    logger.info("모바일 메시지 목록 조회 요청 수신")
    result = await mock_api_request("/mobile/messages")
    return result

@mcp.tool()
async def send_message(title: str, content: str, recipient: str) -> Dict[str, Any]:
    """
    문자 메시지를 보냅니다.
    지정된 수신자에게 제목과 내용을 포함하는 메시지를 전송합니다.
    
    Args:
        title (str): 메시지 제목. 최대 50자까지 입력 가능합니다.
        content (str): 메시지 내용. 최대 500자까지 입력 가능합니다.
        recipient (str): 수신자. 연락처 또는 이름을 입력합니다.
        
    Returns:
        Dict[str, Any]: 작업 결과를 포함하는 딕셔너리
        
    예시 요청:
        send_message(
            title="냉장고 알림", 
            content="냉장고 문이 열려있습니다. 확인해주세요.", 
            recipient="홍길동"
        )
        
    예시 응답:
        {
            "result": "success",
            "message": "메시지가 성공적으로 전송되었습니다.",
            "message_id": 3,
            "timestamp": "2023-04-17T10:45:00"
        }
        
    오류 응답:
        {
            "error": "수신자 정보가 유효하지 않습니다."
        }
    """
    logger.info(f"문자 메시지 전송 요청 수신: 제목: {title}, 수신자: {recipient}")
    data = {
        "title": title,
        "content": content,
        "recipient": recipient
    }
    result = await mock_api_request("/mobile/messages", "POST", data)
    return result

@mcp.tool()
async def delete_message(message_id: int) -> Dict[str, Any]:
    """
    문자 메시지를 삭제합니다.
    지정된 ID의 메시지를 영구적으로 삭제합니다.
    
    Args:
        message_id (int): 삭제할 메시지 ID. get_messages()로 조회한 메시지 목록에서 확인 가능합니다.
        
    Returns:
        Dict[str, Any]: 작업 결과를 포함하는 딕셔너리
        
    예시 요청:
        delete_message(message_id=2)
        
    예시 응답:
        {
            "result": "success",
            "message": "메시지가 성공적으로 삭제되었습니다.",
            "message_id": 2
        }
        
    오류 응답:
        {
            "error": "해당 ID의 메시지를 찾을 수 없습니다."
        }
    """
    logger.info(f"문자 메시지 삭제 요청 수신: ID: {message_id}")
    result = await mock_api_request(f"/mobile/messages/{message_id}", "DELETE")
    return result

@mcp.tool()
async def get_calendar_events() -> Dict[str, Any]:
    """
    캘린더 일정 목록을 조회합니다.
    사용자의 모든 일정을 날짜순으로 정렬하여 반환합니다.
    
    Args:
        없음
        
    Returns:
        Dict[str, Any]: 일정 목록을 포함하는 딕셔너리
        
    예시 요청:
        get_calendar_events()
        
    예시 응답:
        {
            "events": [
                {
                    "id": 1,
                    "title": "스마트홈 시스템 점검",
                    "content": "스마트홈 시스템 전체 정기 점검",
                    "date": "2023-04-20T14:00:00",
                    "is_completed": false
                },
                {
                    "id": 2,
                    "title": "인덕션 수리 예약",
                    "content": "인덕션 화구 작동 이상 수리 방문",
                    "date": "2023-04-25T11:30:00",
                    "is_completed": false
                }
            ],
            "count": 2,
            "message": "2개의 일정이 있습니다."
        }
    """
    logger.info("캘린더 일정 목록 조회 요청 수신")
    result = await mock_api_request("/mobile/calendar")
    return result

@mcp.tool()
async def add_calendar_event(date_str: str, title: str, content: str) -> Dict[str, Any]:
    """
    캘린더 일정을 추가합니다.
    새로운 일정을 캘린더에 추가합니다.
    
    Args:
        date_str (str): 일정 날짜 (YYYY-MM-DDTHH:MM:SS 형식). 예: "2023-04-21T15:30:00"
        title (str): 일정 제목. 최대 100자까지 입력 가능합니다.
        content (str): 일정 내용. 최대 500자까지 입력 가능합니다.
        
    Returns:
        Dict[str, Any]: 작업 결과를 포함하는 딕셔너리
        
    예시 요청:
        add_calendar_event(
            date_str="2023-05-01T09:00:00", 
            title="에어컨 필터 교체", 
            content="거실 및 안방 에어컨 필터 교체 작업"
        )
        
    예시 응답:
        {
            "result": "success",
            "message": "일정이 성공적으로 추가되었습니다.",
            "event_id": 3,
            "event": {
                "id": 3,
                "title": "에어컨 필터 교체",
                "content": "거실 및 안방 에어컨 필터 교체 작업",
                "date": "2023-05-01T09:00:00",
                "is_completed": false
            }
        }
        
    오류 응답:
        {
            "error": "날짜 형식이 올바르지 않습니다. YYYY-MM-DDTHH:MM:SS 형식을 사용하세요."
        }
    """
    logger.info(f"캘린더 일정 추가 요청 수신: 제목: {title}, 날짜: {date_str}")
    try:
        # ISO 8601 형식으로 변환 (YYYY-MM-DDTHH:MM:SS)
        date_obj = datetime.fromisoformat(date_str)
        
        data = {
            "date": date_str,
            "title": title,
            "content": content
        }
        result = await mock_api_request("/mobile/calendar", "POST", data)
        return result
    except ValueError:
        error_msg = "날짜 형식이 올바르지 않습니다. YYYY-MM-DDTHH:MM:SS 형식을 사용하세요."
        logger.error(error_msg)
        return {"error": error_msg}

@mcp.tool()
async def delete_calendar_event(event_id: int) -> Dict[str, Any]:
    """
    캘린더 일정을 삭제합니다.
    지정된 ID의 일정을 영구적으로 삭제합니다.
    
    Args:
        event_id (int): 삭제할 일정 ID. get_calendar_events()로 조회한 일정 목록에서 확인 가능합니다.
        
    Returns:
        Dict[str, Any]: 작업 결과를 포함하는 딕셔너리
        
    예시 요청:
        delete_calendar_event(event_id=2)
        
    예시 응답:
        {
            "result": "success",
            "message": "일정이 성공적으로 삭제되었습니다.",
            "event_id": 2
        }
        
    오류 응답:
        {
            "error": "해당 ID의 일정을 찾을 수 없습니다."
        }
    """
    logger.info(f"캘린더 일정 삭제 요청 수신: ID: {event_id}")
    result = await mock_api_request(f"/mobile/calendar/{event_id}", "DELETE")
    return result

@mcp.tool()
async def set_alarm(time_str: str, title: str, repeat: Optional[str] = None) -> Dict[str, Any]:
    """
    알람을 설정합니다.
    지정된 시간에 울리는 알람을 추가합니다.
    
    Args:
        time_str (str): 알람 시간 (HH:MM 형식). 예: "07:30"
        title (str): 알람 제목. 최대 50자까지 입력 가능합니다.
        repeat (Optional[str]): 알람 반복 주기. 'daily', 'weekdays', 'weekends', 'none' 중 하나.
                               기본값은 'none'(반복 안함)입니다.
        
    Returns:
        Dict[str, Any]: 작업 결과를 포함하는 딕셔너리
        
    예시 요청:
        set_alarm(time_str="07:30", title="기상 알람", repeat="weekdays")
        
    예시 응답:
        {
            "result": "success",
            "message": "알람이 성공적으로 설정되었습니다.",
            "alarm_id": 1,
            "alarm": {
                "id": 1,
                "time": "07:30",
                "title": "기상 알람",
                "repeat": "weekdays",
                "is_active": true
            }
        }
        
    오류 응답:
        {
            "error": "시간 형식이 올바르지 않습니다. HH:MM 형식을 사용하세요."
        }
    """
    logger.info(f"알람 설정 요청 수신: 시간: {time_str}, 제목: {title}")
    
    # 시간 형식 검증
    try:
        hour, minute = map(int, time_str.split(':'))
        if hour < 0 or hour > 23 or minute < 0 or minute > 59:
            raise ValueError("시간 범위 오류")
            
        data = {
            "time": time_str,
            "title": title,
            "repeat": repeat or "none"
        }
        result = await mock_api_request("/mobile/alarms", "POST", data)
        return result
    except (ValueError, AttributeError):
        error_msg = "시간 형식이 올바르지 않습니다. HH:MM 형식을 사용하세요."
        logger.error(error_msg)
        return {"error": error_msg}

@mcp.tool()
async def get_alarms() -> Dict[str, Any]:
    """
    설정된 알람 목록을 조회합니다.
    사용자의 모든 알람을 시간순으로 정렬하여 반환합니다.
    
    Args:
        없음
        
    Returns:
        Dict[str, Any]: 알람 목록을 포함하는 딕셔너리
        
    예시 요청:
        get_alarms()
        
    예시 응답:
        {
            "alarms": [
                {
                    "id": 1,
                    "time": "07:30",
                    "title": "기상 알람",
                    "repeat": "weekdays",
                    "is_active": true
                },
                {
                    "id": 2,
                    "time": "22:00",
                    "title": "취침 알람",
                    "repeat": "daily",
                    "is_active": true
                }
            ],
            "count": 2,
            "message": "2개의 알람이 설정되어 있습니다."
        }
    """
    logger.info("알람 목록 조회 요청 수신")
    result = await mock_api_request("/mobile/alarms")
    return result

if __name__ == "__main__":
    # 서버 시작 메시지 출력
    print("모바일 MCP 서버가 실행 중입니다...")
    
    # SSE 트랜스포트를 사용하여 MCP 서버 시작
    mcp.run(transport="sse") 