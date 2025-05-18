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
LIGHT_MCP_NAME = os.environ.get("LIGHT_MCP_NAME", "light")
LIGHT_MCP_HOST = os.environ.get("LIGHT_MCP_HOST", "0.0.0.0")
LIGHT_MCP_PORT = int(os.environ.get("LIGHT_MCP_PORT", 10008))
LIGHT_MCP_INSTRUCTIONS = os.environ.get("LIGHT_MCP_INSTRUCTIONS", "조명 관련 기능을 제어하는 도구입니다. 조명 전원 제어, 밝기 조절, 색상 변경, 모드 설정, 상태 확인 등의 기능을 제공합니다.")

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("light_mcp_server")

# FastMCP 인스턴스 생성
mcp = FastMCP(
    LIGHT_MCP_NAME,  # MCP 서버 이름
    instructions=LIGHT_MCP_INSTRUCTIONS,
    host=LIGHT_MCP_HOST,  # 모든 IP에서 접속 허용
    port=LIGHT_MCP_PORT,  # 포트 번호
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
async def get_light_status() -> Dict[str, Any]:
    """
    조명의 현재 상태를 조회합니다.
    
    이 도구는 조명의 현재 전원 상태, 밝기 레벨, 색상, 모드 등
    전반적인 상태 정보를 반환합니다.
    
    Returns:
        Dict[str, Any]: 조명 상태 정보를 포함하는 딕셔너리 형태의 응답
        
    응답에 포함되는 정보:
        - power: 조명의 전원 상태 (true: 켜짐, false: 꺼짐)
        - brightness: 현재 밝기 레벨 (0-100%)
        - color: 현재 색상 (예: "warm", "cool", "blue" 등)
        - mode: 현재 설정된 모드 (예: "normal", "study", "relax" 등)
        - message: 조명 상태를 설명하는 메시지
        
    예시 응답:
        {
            "power": true,
            "brightness": 75,
            "color": "warm",
            "mode": "relaxation",
            "message": "조명이 켜져 있으며, 밝기 75%, 따뜻한 색상, 휴식 모드입니다."
        }
    """
    logger.info("조명 상태 조회 요청 수신")
    result = await mock_api_request("/light/status", "GET")
    return result

@mcp.tool()
async def set_light_power(power_state: str) -> Dict[str, Any]:
    """
    조명 전원을 켜거나 끕니다.
    
    이 도구는 조명의 전원 상태를 제어합니다. 조명이 꺼져 있을 때 켜거나,
    켜져 있을 때 끌 수 있습니다.
    
    Args:
        power_state (str): "on" 또는 "off" 값만 허용됩니다.
            - "on": 조명을 켭니다. 이전 밝기, 색상, 모드 설정이 유지됩니다.
            - "off": 조명을 끕니다. 설정값은 유지되지만 빛이 꺼집니다.
        
    Returns:
        Dict[str, Any]: 조명 전원 제어 결과를 포함하는 딕셔너리 형태의 응답
            - result: 작업 결과 상태 ("success", "error" 등)
            - message: 결과 설명 메시지
    
    예시:
        set_light_power("on") -> 조명을 켭니다.
        set_light_power("off") -> 조명을 끕니다.
    """
    logger.info(f"조명 전원 제어 요청 수신: {power_state}")
    if power_state not in ["on", "off"]:
        return {"error": "전원 상태는 'on' 또는 'off'여야 합니다."}
    
    result = await mock_api_request("/light/power", "POST", {"power_state": power_state})
    return result

@mcp.tool()
async def set_light_brightness(level: int) -> Dict[str, Any]:
    """
    조명 밝기를 조절합니다.
    
    이 도구는 조명의 밝기 레벨을 조정합니다. 밝기는 0(꺼짐)부터 100(최대 밝기)까지의
    정수 값으로 설정할 수 있으며, 조명이 켜져 있는 상태에서만 조절 가능합니다.
    
    Args:
        level (int): 밝기 값 (0~100 사이의 정수)
            - 0: 가장 어두움 (거의 꺼진 상태)
            - 50: 중간 밝기
            - 100: 최대 밝기
        
    Returns:
        Dict[str, Any]: 밝기 조절 결과를 포함하는 딕셔너리 형태의 응답
            - result: 작업 결과 상태 ("success", "error" 등)
            - message: 결과 설명 메시지
    
    참고:
        조명이 꺼져 있는 경우에는 밝기를 조절할 수 없으며 오류가 반환됩니다.
        밝기를 0으로 설정하는 것은 조명을 끄는 것과는 다르며, 매우 어두운 상태입니다.
    
    예시:
        set_light_brightness(30) -> 조명 밝기를 30%로 설정합니다.
        set_light_brightness(80) -> 조명 밝기를 80%로 밝게 설정합니다.
        set_light_brightness(100) -> 조명 밝기를 최대로 설정합니다.
    """
    logger.info(f"조명 밝기 조절 요청 수신: {level}")
    if not (0 <= level <= 100):
        return {"error": "밝기 값은 0에서 100 사이여야 합니다."}
    
    result = await mock_api_request("/light/brightness", "POST", {"level": level})
    return result

@mcp.tool()
async def set_light_color(color: str) -> Dict[str, Any]:
    """
    조명 색상을 변경합니다.
    
    이 도구는 조명의 색상을 변경합니다. 다양한 사전 정의된 색상 중에서
    선택할 수 있으며, 조명이 켜져 있는 상태에서만 변경 가능합니다.
    
    Args:
        color (str): 색상명 (예: "warm", "cool", "blue", "red", "green" 등)
            - "warm": 따뜻한 노란색/주황색 계열 (2700K-3000K) - 편안하고 아늑한 분위기
            - "cool": 시원한 흰색 계열 (4000K-5000K) - 집중력을 높이는 분위기
            - "blue": 푸른색 계열 - 진정 및 안정감을 주는 분위기
            - "red": 붉은색 계열 - 따뜻하고 강렬한 분위기
            - "green": 녹색 계열 - 자연스럽고 편안한 분위기
        
    Returns:
        Dict[str, Any]: 색상 변경 결과를 포함하는 딕셔너리 형태의 응답
            - result: 작업 결과 상태 ("success", "error" 등)
            - message: 결과 설명 메시지
    
    참고:
        조명이 꺼져 있는 경우에는 색상을 변경할 수 없으며 오류가 반환됩니다.
        색상은 모델에 따라 지원 여부가 다를 수 있습니다.
    
    예시:
        set_light_color("warm") -> 조명 색상을 따뜻한 노란색으로 변경합니다.
        set_light_color("cool") -> 조명 색상을 시원한 흰색으로 변경합니다.
        set_light_color("blue") -> 조명 색상을 푸른색으로 변경합니다.
    """
    logger.info(f"조명 색상 변경 요청 수신: {color}")
    result = await mock_api_request("/light/color", "POST", {"color": color})
    return result

@mcp.tool()
async def set_light_mode(mode: str) -> Dict[str, Any]:
    """
    조명 프리셋 모드를 적용합니다.
    
    이 도구는 조명에 미리 정의된 프리셋 모드를 적용합니다. 각 모드는 특정 활동이나
    분위기에 맞게 밝기, 색상 등이 최적화되어 있습니다.
    
    Args:
        mode (str): 프리셋 모드명 (예: "study", "relax", "healing", "reading" 등)
            - "study": 학습/작업에 최적화된 밝고 집중력을 높이는 조명 (밝기 높음, 차가운 색상)
            - "relax": 휴식에 최적화된 편안한 조명 (중간 밝기, 따뜻한 색상)
            - "healing": 힐링/명상에 최적화된 부드러운 조명 (밝기 낮음, 푸른색 계열)
            - "reading": 독서에 최적화된 조명 (중간-높은 밝기, 중간색온도)
            - "normal": 일반적인 일상 활동에 적합한 표준 조명 (중간 밝기, 중간색온도)
        
    Returns:
        Dict[str, Any]: 모드 적용 결과를 포함하는 딕셔너리 형태의 응답
            - result: 작업 결과 상태 ("success", "error" 등)
            - message: 결과 설명 메시지
    
    참고:
        조명이 꺼져 있는 경우에는 모드를 변경할 수 없으며 오류가 반환됩니다.
        모드를 변경하면 이전에 수동으로 설정한 밝기나 색상 등의 설정이 모드에 맞게 자동으로 변경됩니다.
    
    예시:
        set_light_mode("study") -> 학습에 최적화된 밝은 조명 모드로 변경합니다.
        set_light_mode("relax") -> 휴식에 적합한 따뜻하고 부드러운 조명 모드로 변경합니다.
    """
    logger.info(f"조명 모드 적용 요청 수신: {mode}")
    result = await mock_api_request("/light/mode", "POST", {"mode": mode})
    return result

if __name__ == "__main__":
    # 서버 시작 메시지 출력
    print("조명 MCP 서버가 실행 중입니다...")
    
    # SSE 트랜스포트를 사용하여 MCP 서버 시작
    mcp.run(transport="sse") 