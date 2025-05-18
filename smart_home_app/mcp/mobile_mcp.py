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
MOBILE_MCP_INSTRUCTIONS = os.environ.get("MOBILE_MCP_INSTRUCTIONS", "모바일 기능을 제어하는 도구입니다. 메시지 조회/전송/삭제, 캘린더 일정 조회/추가/삭제 등의 기능을 제공합니다.")

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
    
    Returns:
        Dict[str, Any]: 메시지 목록
    """
    logger.info("모바일 메시지 목록 조회 요청 수신")
    result = await mock_api_request("/mobile/messages")
    return result

@mcp.tool()
async def send_message(title: str, content: str, recipient: str) -> Dict[str, Any]:
    """
    문자 메시지를 보냅니다.
    
    Args:
        title (str): 메시지 제목
        content (str): 메시지 내용
        recipient (str): 수신자
        
    Returns:
        Dict[str, Any]: 작업 결과
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
    
    Args:
        message_id (int): 삭제할 메시지 ID
        
    Returns:
        Dict[str, Any]: 작업 결과
    """
    logger.info(f"문자 메시지 삭제 요청 수신: ID: {message_id}")
    result = await mock_api_request(f"/mobile/messages/{message_id}", "DELETE")
    return result

@mcp.tool()
async def get_calendar_events() -> Dict[str, Any]:
    """
    캘린더 일정 목록을 조회합니다.
    
    Returns:
        Dict[str, Any]: 일정 목록
    """
    logger.info("캘린더 일정 목록 조회 요청 수신")
    result = await mock_api_request("/mobile/calendar")
    return result

@mcp.tool()
async def add_calendar_event(date_str: str, title: str, content: str) -> Dict[str, Any]:
    """
    캘린더 일정을 추가합니다.
    
    Args:
        date_str (str): 일정 날짜 (YYYY-MM-DDTHH:MM:SS 형식)
        title (str): 일정 제목
        content (str): 일정 내용
        
    Returns:
        Dict[str, Any]: 작업 결과
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
    
    Args:
        event_id (int): 삭제할 일정 ID
        
    Returns:
        Dict[str, Any]: 작업 결과
    """
    logger.info(f"캘린더 일정 삭제 요청 수신: ID: {event_id}")
    result = await mock_api_request(f"/mobile/calendar/{event_id}", "DELETE")
    return result

if __name__ == "__main__":
    # 서버 시작 메시지 출력
    print("모바일 MCP 서버가 실행 중입니다...")
    
    # SSE 트랜스포트를 사용하여 MCP 서버 시작
    mcp.run(transport="sse") 