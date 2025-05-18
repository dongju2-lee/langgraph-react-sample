from mcp.server.fastmcp import FastMCP
import os
import requests
import json
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()
MOCK_SERVER_URL = os.environ.get("MOCK_SERVER_URL", "http://localhost:10000")
CURTAIN_MCP_NAME = os.environ.get("CURTAIN_MCP_NAME", "curtain")
CURTAIN_MCP_HOST = os.environ.get("CURTAIN_MCP_HOST", "0.0.0.0")
CURTAIN_MCP_PORT = int(os.environ.get("CURTAIN_MCP_PORT", 10009))
CURTAIN_MCP_INSTRUCTIONS = os.environ.get("CURTAIN_MCP_INSTRUCTIONS", "커튼 관련 기능을 제어하는 도구입니다. 커튼 열기/닫기, 부분 열기, 스케줄 설정, 상태 확인 등의 기능을 제공합니다.")

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("curtain_mcp_server")

# FastMCP 인스턴스 생성
mcp = FastMCP(
    CURTAIN_MCP_NAME,  # MCP 서버 이름
    instructions=CURTAIN_MCP_INSTRUCTIONS,
    host=CURTAIN_MCP_HOST,  # 모든 IP에서 접속 허용
    port=CURTAIN_MCP_PORT,  # 포트 번호
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
async def get_curtain_status() -> Dict[str, Any]:
    """
    현재 커튼의 상태를 조회합니다.
    
    이 도구는 커튼의 현재 상태 정보를 반환합니다. 여기에는 열림/닫힘 상태,
    열린 정도(퍼센트), 설정된 스케줄 정보 등이 포함됩니다.
    
    Returns:
        Dict[str, Any]: 커튼 상태 정보를 포함하는 딕셔너리 형태의 응답
    
    응답에 포함되는 정보:
        - power_state: 커튼의 현재 상태 ("open" 또는 "close")
        - position: 커튼이 열려있는 정도(0~100%, 0은 완전히 닫힘, 100은 완전히 열림)
        - is_open: 커튼이 열려 있는지 여부(Boolean)
        - schedules: 설정된 스케줄 목록
        - message: 상태를 설명하는 메시지
    
    예시 응답:
        {
            "power_state": "open",
            "position": 100,
            "is_open": true,
            "schedules": [{"time": "08:00", "action": "open"}],
            "message": "커튼이 완전히 열려 있습니다."
        }
    """
    logger.info("커튼 상태 조회 요청 수신")
    result = await mock_api_request("/curtain/status", "GET")
    return result

@mcp.tool()
async def set_curtain_power(power_state: str) -> Dict[str, Any]:
    """
    커튼을 완전히 열거나 닫습니다.
    
    이 도구는 커튼을 완전히 열거나 완전히 닫는 기능을 제공합니다.
    "open"을 선택하면 커튼이 100% 열리고, "close"를 선택하면 완전히 닫힙니다.
    
    Args:
        power_state (str): "open" 또는 "close" 값만 허용됩니다.
            - "open": 커튼을 완전히 엽니다 (position=100%).
            - "close": 커튼을 완전히 닫습니다 (position=0%).
        
    Returns:
        Dict[str, Any]: 커튼 제어 결과를 포함하는 딕셔너리 형태의 응답
            - result: 작업 결과 상태 ("success", "error" 등)
            - message: 결과 설명 메시지
    
    예시:
        set_curtain_power("open") -> 커튼을 완전히 엽니다.
        set_curtain_power("close") -> 커튼을 완전히 닫습니다.
    """
    logger.info(f"커튼 전원 제어 요청 수신: {power_state}")
    if power_state not in ["open", "close"]:
        return {"error": "전원 상태는 'open' 또는 'close'여야 합니다."}
    
    result = await mock_api_request("/curtain/power", "POST", {"power_state": power_state})
    return result

@mcp.tool()
async def set_curtain_position(percent: int) -> Dict[str, Any]:
    """
    커튼을 지정한 비율(%)만큼 열거나 닫습니다.
    
    이 도구는 커튼을 지정된 퍼센트만큼 부분적으로 열거나 닫습니다.
    0%는 완전히 닫힌 상태, 100%는 완전히 열린 상태를 의미합니다.
    
    Args:
        percent (int): 커튼을 열 비율 (0~100 사이의 정수)
            - 0: 완전히 닫힘
            - 50: 절반 열림
            - 100: 완전히 열림
        
    Returns:
        Dict[str, Any]: 커튼 위치 제어 결과를 포함하는 딕셔너리 형태의 응답
            - result: 작업 결과 상태 ("success", "error" 등)
            - message: 결과 설명 메시지
    
    참고:
        percent가 0이면 power_state는 "close"로 설정됩니다.
        percent가 100이면 power_state는 "open"으로 설정됩니다.
        중간 값(1-99)인 경우 부분적으로 열린 상태가 됩니다.
    """
    logger.info(f"커튼 위치 제어 요청 수신: {percent}%")
    if not (0 <= percent <= 100):
        return {"error": "커튼 위치 값은 0에서 100 사이여야 합니다."}
    
    result = await mock_api_request("/curtain/position", "POST", {"percent": percent})
    return result

@mcp.tool()
async def set_curtain_schedule(time: str, action: str) -> Dict[str, Any]:
    """
    지정한 시간에 커튼을 자동으로 열거나 닫도록 예약합니다.
    
    이 도구는 특정 시간에 커튼이 자동으로 열리거나 닫히도록 스케줄을 설정합니다.
    정해진 시간이 되면 시스템이 자동으로 커튼을 제어합니다.
    
    Args:
        time (str): 예약 시간. "HH:MM" 형식으로 지정. (예: "08:00", "18:30")
            - 24시간 형식을 사용합니다.
            - 올바른 시간 형식이 아닌 경우 오류가 발생할 수 있습니다.
        action (str): 수행할 동작. "open" 또는 "close"만 허용됩니다.
            - "open": 지정된 시간에 커튼을 엽니다.
            - "close": 지정된 시간에 커튼을 닫습니다.
        
    Returns:
        Dict[str, Any]: 커튼 스케줄 설정 결과를 포함하는 딕셔너리 형태의 응답
            - result: 작업 결과 상태 ("success", "error" 등)
            - message: 결과 설명 메시지
    
    참고:
        같은 시간에 이미 다른 스케줄이 설정되어 있으면 새 스케줄로 덮어씁니다.
        새 시간에 스케줄을 설정하면 기존 스케줄은 그대로 유지되고 새 스케줄이 추가됩니다.
    
    예시:
        set_curtain_schedule("08:00", "open") -> 매일 오전 8시에 커튼이 자동으로 열립니다.
        set_curtain_schedule("22:30", "close") -> 매일 밤 10시 30분에 커튼이 자동으로 닫힙니다.
    """
    logger.info(f"커튼 스케줄 설정 요청 수신: {time} {action}")
    if action not in ["open", "close"]:
        return {"error": "동작은 'open' 또는 'close'여야 합니다."}
    
    result = await mock_api_request("/curtain/schedule", "POST", {"time": time, "action": action})
    return result

if __name__ == "__main__":
    # 서버 시작 메시지 출력
    print("커튼 MCP 서버가 실행 중입니다...")
    
    # SSE 트랜스포트를 사용하여 MCP 서버 시작
    mcp.run(transport="sse") 