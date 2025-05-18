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
INDUCTION_MCP_NAME = os.environ.get("INDUCTION_MCP_NAME", "induction")
INDUCTION_MCP_HOST = os.environ.get("INDUCTION_MCP_HOST", "0.0.0.0")
INDUCTION_MCP_PORT = int(os.environ.get("INDUCTION_MCP_PORT", 10002))
INDUCTION_MCP_INSTRUCTIONS = os.environ.get("INDUCTION_MCP_INSTRUCTIONS", "인덕션을 제어하는 도구입니다. 전원 상태 확인, 전원 상태 변경, 조리 시작, 조리 중단, 화력 조절 등의 기능을 제공합니다.")

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("induction_mcp_server")

# FastMCP 인스턴스 생성
mcp = FastMCP(
    INDUCTION_MCP_NAME,  # MCP 서버 이름
    instructions=INDUCTION_MCP_INSTRUCTIONS,
    host=INDUCTION_MCP_HOST,  # 모든 IP에서 접속 허용
    port=INDUCTION_MCP_PORT,  # 포트 번호
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
async def get_induction_status() -> Dict[str, Any]:
    """
    인덕션의 현재 상태를 조회합니다.
    
    이 도구는 인덕션의 현재 전원 상태, 조리 중 여부, 화력 단계 등의
    전반적인 상태 정보를 반환합니다.
    
    Returns:
        Dict[str, Any]: 인덕션 상태 정보를 포함하는 딕셔너리 형태의 응답
        
    응답에 포함되는 정보:
        - power: 인덕션의 전원 상태 (true: 켜짐, false: 꺼짐)
        - cooking: 조리 중 여부 (true: 조리 중, false: 조리 중이 아님)
        - heat_level: 현재 설정된 화력 단계 ("HIGH", "MEDIUM", "LOW" 중 하나)
        - message: 인덕션 상태를 설명하는 메시지
        
    예시 응답:
        {
            "power": true,
            "cooking": true,
            "heat_level": "HIGH",
            "message": "인덕션이 강불로 조리 중입니다."
        }
        
        또는 (전원이 꺼진 경우):
        {
            "power": false,
            "cooking": false,
            "heat_level": null,
            "message": "인덕션 전원이 꺼져 있습니다."
        }
    """
    logger.info("인덕션 상태 조회 요청 수신")
    result = await mock_api_request("/api/induction/status")
    return result

@mcp.tool()
async def toggle_induction_power() -> Dict[str, Any]:
    """
    인덕션 전원을 켜거나 끕니다.
    
    이 도구는 인덕션의 전원 상태를 토글합니다. 현재 켜져 있으면 끄고, 
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
            "message": "인덕션 전원이 켜졌습니다"
        }
    
    예시 응답 (끌 때):
        {
            "result": "success",
            "power": false,
            "message": "인덕션 전원이 꺼졌습니다"
        }
    
    참고:
        전원을 껐을 때 조리 중이었다면 조리가 자동으로 중단됩니다.
        이 함수는 현재 상태의 반대로 전환하는 토글 방식으로 동작합니다.
    """
    logger.info("인덕션 전원 토글 요청 수신")
    result = await mock_api_request("/api/induction/power", "POST")
    return result

@mcp.tool()
async def start_induction_cooking(heat_level: str) -> Dict[str, Any]:
    """
    인덕션 조리를 시작합니다.
    
    이 도구는 인덕션 조리를 시작하며, 지정된 화력으로 인덕션을 작동시킵니다.
    조리를 시작하기 위해서는 먼저 인덕션 전원이 켜져 있어야 합니다.
    
    Args:
        heat_level (str): 화력 수준을 지정합니다. 다음 값들만 허용됩니다:
            - "HIGH" 또는 "강불": 가장 높은 화력으로 조리합니다. 볶음요리, 물 끓이기에 적합합니다.
            - "MEDIUM" 또는 "중불": 중간 화력으로 조리합니다. 일반 요리에 적합합니다.
            - "LOW" 또는 "약불": 낮은 화력으로 천천히 조리합니다. 오래 끓이는 요리, 소스 만들기에 적합합니다.
        
    Returns:
        Dict[str, Any]: 조리 시작 결과를 포함하는 딕셔너리 형태의 응답
            - result: 작업 결과 상태 ("success", "error" 등)
            - cooking: 조리 시작 성공 여부 (true/false)
            - heat_level: 설정된 화력 레벨
            - message: 결과 설명 메시지
    
    예시 응답 (성공 시):
        {
            "result": "success",
            "cooking": true,
            "heat_level": "HIGH",
            "message": "인덕션이 강불로 조리를 시작했습니다."
        }
    
    예시 응답 (오류 시):
        {
            "result": "error",
            "message": "인덕션 전원이 꺼져 있어 조리를 시작할 수 없습니다."
        }
    
    참고:
        전원이 꺼져 있는 상태에서는 조리를 시작할 수 없으며 오류가 반환됩니다.
        먼저 toggle_induction_power()를 호출하여 전원을 켜야 합니다.
    """
    logger.info(f"인덕션 조리 시작 요청 수신: 화력 {heat_level}")
    # 한글 화력을 영어로 변환
    heat_level_map = {"강불": "HIGH", "중불": "MEDIUM", "약불": "LOW"}
    
    if heat_level in heat_level_map:
        heat_level = heat_level_map[heat_level]
    elif heat_level not in ["HIGH", "MEDIUM", "LOW"]:
        return {"error": "화력은 'HIGH(강불)', 'MEDIUM(중불)', 'LOW(약불)' 중 하나여야 합니다."}
    
    result = await mock_api_request("/api/induction/start-cooking", "POST", {"heat_level": heat_level})
    return result

@mcp.tool()
async def stop_induction_cooking() -> Dict[str, Any]:
    """
    인덕션 조리를 중단합니다.
    
    이 도구는 현재 진행 중인 인덕션 조리를 즉시 중단합니다. 인덕션의 전원은 
    그대로 켜진 상태로 유지되며, 단지 가열 과정만 중단됩니다.
    
    Returns:
        Dict[str, Any]: 조리 중단 결과를 포함하는 딕셔너리 형태의 응답
            - result: 작업 결과 상태 ("success", "error", "info" 등)
            - cooking: 중단 후 조리 상태 (항상 false)
            - message: 결과 설명 메시지
    
    예시 응답 (조리 중이었을 때):
        {
            "result": "success",
            "cooking": false,
            "message": "인덕션 조리가 중단되었습니다."
        }
    
    예시 응답 (이미 조리 중이 아니었을 때):
        {
            "result": "info",
            "cooking": false,
            "message": "인덕션이 이미 조리 중이 아닙니다."
        }
    
    참고:
        조리 중이 아닌 상태에서 호출해도 오류가 발생하지 않고 결과 값만 달라집니다.
        인덕션 전원은 계속 켜져 있으며, 필요 시 toggle_induction_power()를 별도로 호출해야 합니다.
    """
    logger.info("인덕션 조리 중단 요청 수신")
    result = await mock_api_request("/api/induction/stop-cooking", "POST")
    return result

if __name__ == "__main__":
    # 서버 시작 메시지 출력
    print("인덕션 MCP 서버가 실행 중입니다...")
    
    # SSE 트랜스포트를 사용하여 MCP 서버 시작
    mcp.run(transport="sse") 