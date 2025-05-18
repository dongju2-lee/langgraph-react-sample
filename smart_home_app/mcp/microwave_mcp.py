import json
import requests
from typing import Dict, Any, Optional
from mcp.server.fastmcp import FastMCP
import os
import logging
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()
MOCK_SERVER_URL = os.environ.get("MOCK_SERVER_URL", "http://localhost:10000")
MICROWAVE_MCP_NAME = os.environ.get("MICROWAVE_MCP_NAME", "microwave")
MICROWAVE_MCP_HOST = os.environ.get("MICROWAVE_MCP_HOST", "0.0.0.0")
MICROWAVE_MCP_PORT = int(os.environ.get("MICROWAVE_MCP_PORT", 10003))
MICROWAVE_MCP_INSTRUCTIONS = os.environ.get("MICROWAVE_MCP_INSTRUCTIONS", "전자레인지를 제어하는 도구입니다. 전원 상태 확인, 전원 상태 변경, 조리 시작, 조리 중단, 남은 시간 확인 등의 기능을 제공합니다.")

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("microwave_mcp_server")

# FastMCP 인스턴스 생성
mcp = FastMCP(
    MICROWAVE_MCP_NAME,  # MCP 서버 이름
    instructions=MICROWAVE_MCP_INSTRUCTIONS,
    host=MICROWAVE_MCP_HOST,  # 모든 IP에서 접속 허용
    port=MICROWAVE_MCP_PORT,  # 포트 번호
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
async def get_microwave_status() -> Dict[str, Any]:
    """
    전자레인지의 현재 상태를 조회합니다.
    
    이 도구는 전자레인지의 현재 전원 상태, 조리 중 여부, 남은 조리 시간 등의
    전반적인 상태 정보를 반환합니다.
    
    Returns:
        Dict[str, Any]: 전자레인지 상태 정보를 포함하는 딕셔너리 형태의 응답
        
    응답에 포함되는 정보:
        - power: 전자레인지 전원 상태 (true: 켜짐, false: 꺼짐)
        - cooking: 조리 중 여부 (true: 조리 중, false: 조리 중이 아님)
        - remaining_seconds: 남은 조리 시간(초) (조리 중일 때만 포함)
        - message: 전자레인지 상태를 설명하는 메시지
        
    예시 응답 (조리 중일 때):
        {
            "power": true,
            "cooking": true,
            "remaining_seconds": 45,
            "message": "조리 중: 남은 시간 45초"
        }
        
    예시 응답 (전원은 켜져 있지만 조리 중이 아닐 때):
        {
            "power": true,
            "cooking": false,
            "message": "전원이 켜져 있으나 조리 중이 아닙니다."
        }
        
    예시 응답 (전원이 꺼져 있을 때):
        {
            "power": false,
            "cooking": false,
            "message": "전자레인지 전원이 꺼져 있습니다."
        }
    """
    logger.info("전자레인지 상태 조회 요청 수신")
    result = await mock_api_request("/api/microwave/status")
    return result

@mcp.tool()
async def toggle_microwave_power() -> Dict[str, Any]:
    """
    전자레인지 전원을 켜거나 끕니다.
    
    이 도구는 전자레인지의 전원 상태를 토글합니다. 현재 켜져 있으면 끄고, 
    꺼져 있으면 켭니다. 전원이 꺼지면 조리 중이던 작업도 함께 중단됩니다.
    
    Returns:
        Dict[str, Any]: 전원 제어 결과를 포함하는 딕셔너리 형태의 응답
            - result: 작업 결과 상태 ("success", "error" 등)
            - power: 변경 후 전원 상태 (true/false)
            - message: 결과 설명 메시지
    
    예시 응답 (켤 때):
        {
            "result": "success",
            "power": true,
            "message": "전자레인지 전원이 켜졌습니다"
        }
    
    예시 응답 (끌 때):
        {
            "result": "success",
            "power": false,
            "message": "전자레인지 전원이 꺼졌습니다"
        }
    
    참고:
        전원을 껐을 때 조리 중이었다면 조리가 자동으로 중단됩니다.
        이 함수는 현재 상태의 반대로 전환하는 토글 방식으로 동작합니다.
    """
    logger.info("전자레인지 전원 토글 요청 수신")
    result = await mock_api_request("/api/microwave/power", "POST")
    return result

@mcp.tool()
async def start_microwave_cooking(seconds: int) -> Dict[str, Any]:
    """
    전자레인지 조리를 시작합니다.
    
    이 도구는 전자레인지 조리를 시작하며, 지정된 시간(초) 동안 조리를 진행합니다.
    조리를 시작하기 위해서는 먼저 전자레인지 전원이 켜져 있어야 합니다.
    
    Args:
        seconds (int): 조리 시간(초). 1 이상의 정수여야 합니다.
            - 일반적인 설정값: 30초(음료 데우기), 60초(간단한 식품), 120초(냉동식품), 180초(육류)
        
    Returns:
        Dict[str, Any]: 조리 시작 결과를 포함하는 딕셔너리 형태의 응답
            - result: 작업 결과 상태 ("success", "error" 등)
            - cooking: 조리 시작 성공 여부 (true/false)
            - duration: 설정된 조리 시간(초)
            - message: 결과 설명 메시지
    
    예시 응답 (성공 시):
        {
            "result": "success",
            "cooking": true,
            "duration": 60,
            "message": "전자레인지 조리가 60초 동안 시작되었습니다."
        }
    
    예시 응답 (오류 시):
        {
            "result": "error",
            "message": "전자레인지 전원이 꺼져 있습니다. 먼저 전원을 켜주세요."
        }
        
        또는
        
        {
            "result": "error",
            "message": "조리 시간은 0보다 커야 합니다."
        }
    
    참고:
        이미 조리 중인 상태에서 이 함수를 호출하면 오류가 발생할 수 있습니다.
        전원이 꺼져 있는 상태에서는 조리를 시작할 수 없습니다.
    """
    logger.info(f"전자레인지 조리 시작 요청 수신: {seconds}초")
    
    if seconds <= 0:
        logger.error("조리 시간은 0보다 커야 합니다.")
        return {"error": "조리 시간은 0보다 커야 합니다."}
    
    result = await mock_api_request("/api/microwave/start", "POST", {"seconds": seconds})
    return result

@mcp.tool()
async def stop_microwave_cooking() -> Dict[str, Any]:
    """
    전자레인지 조리를 중단합니다.
    
    이 도구는 현재 진행 중인 전자레인지 조리를 즉시 중단합니다. 전자레인지의 전원은 
    그대로 켜진 상태로 유지되며, 단지 조리 과정만 중단됩니다.
    
    Returns:
        Dict[str, Any]: 조리 중단 결과를 포함하는 딕셔너리 형태의 응답
            - result: 작업 결과 상태 ("success", "error", "info" 등)
            - cooking: 중단 후 조리 상태 (항상 false)
            - message: 결과 설명 메시지
    
    예시 응답 (조리 중이었을 때):
        {
            "result": "success",
            "cooking": false,
            "message": "전자레인지 조리가 중단되었습니다."
        }
    
    예시 응답 (이미 조리 중이 아니었을 때):
        {
            "result": "info",
            "cooking": false,
            "message": "전자레인지가 이미 조리 중이 아닙니다."
        }
    
    참고:
        조리 중이 아닌 상태에서 호출해도 오류가 발생하지 않고 결과 값만 달라집니다.
        전자레인지 전원은 계속 켜져 있으며, 필요 시 toggle_microwave_power()를 별도로 호출해야 합니다.
    """
    logger.info("전자레인지 조리 중단 요청 수신")
    result = await mock_api_request("/api/microwave/stop", "POST")
    return result

@mcp.tool()
async def get_microwave_remaining_time() -> Dict[str, Any]:
    """
    전자레인지 조리 중 남은 시간을 조회합니다.
    
    이 도구는 현재 전자레인지 조리 중일 경우 남은 시간(초)을 조회합니다.
    전자레인지가 조리 중이 아닌 경우 남은 시간은 0으로 반환됩니다.
    
    Returns:
        Dict[str, Any]: 남은 조리 시간 정보를 포함하는 딕셔너리 형태의 응답
            - remaining_seconds: 남은 조리 시간(초)
            - cooking: 조리 중 여부 (true/false)
            - message: 설명 메시지
    
    예시 응답 (조리 중일 때):
        {
            "remaining_seconds": 42,
            "cooking": true,
            "message": "조리 중: 남은 시간 42초"
        }
    
    예시 응답 (조리 중이 아닐 때):
        {
            "remaining_seconds": 0,
            "cooking": false,
            "message": "조리 중이 아니거나 남은 시간 정보가 없습니다."
        }
    
    참고:
        이 함수는 get_microwave_status()와 유사하지만, 조리 중 남은 시간에 초점을 맞춰 
        관련 정보만 반환하도록 최적화되어 있습니다.
    """
    logger.info("전자레인지 남은 시간 조회 요청 수신")
    result = await mock_api_request("/api/microwave/status")
    
    status = result
    if "remaining_seconds" in status:
        return {
            "remaining_seconds": status["remaining_seconds"],
            "cooking": status["cooking"],
            "message": status["message"]
        }
    else:
        return {
            "remaining_seconds": 0,
            "cooking": status["cooking"],
            "message": "조리 중이 아니거나 남은 시간 정보가 없습니다."
        }

if __name__ == "__main__":
    # 서버 시작 메시지 출력
    print("전자레인지 MCP 서버가 실행 중입니다...")
    
    # SSE 트랜스포트를 사용하여 MCP 서버 시작
    mcp.run(transport="sse") 