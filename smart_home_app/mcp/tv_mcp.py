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
TV_MCP_NAME = os.environ.get("TV_MCP_NAME", "tv")
TV_MCP_HOST = os.environ.get("TV_MCP_HOST", "0.0.0.0")
TV_MCP_PORT = int(os.environ.get("TV_MCP_PORT", 10006))
TV_MCP_INSTRUCTIONS = os.environ.get("TV_MCP_INSTRUCTIONS", "TV 관련 기능을 제어하는 도구입니다. TV 전원 제어, 채널 변경, 볼륨 조절, 채널 목록 조회, 상태 확인 등의 기능을 제공합니다.")

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("tv_mcp_server")

# FastMCP 인스턴스 생성
mcp = FastMCP(
    TV_MCP_NAME,  # MCP 서버 이름
    instructions=TV_MCP_INSTRUCTIONS,
    host=TV_MCP_HOST,  # 모든 IP에서 접속 허용
    port=TV_MCP_PORT,  # 포트 번호
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
async def get_tv_status() -> Dict[str, Any]:
    """
    TV의 현재 상태를 조회합니다.
    
    이 도구는 TV의 현재 전원 상태, 현재 시청 중인 채널, 볼륨 수준 등 
    TV의 전반적인 상태 정보를 반환합니다.
    
    Returns:
        Dict[str, Any]: TV 상태 정보를 포함하는 딕셔너리 형태의 응답
        
    응답에 포함되는 정보:
        - power: TV의 전원 상태 (true: 켜짐, false: 꺼짐)
        - current_channel: 현재 시청 중인 채널 이름
        - volume: 현재 볼륨 레벨 (0-100)
        - message: TV 상태를 설명하는 메시지
        - channel_info: 현재 채널에 대한 상세 정보(TV가 켜져 있을 때만)
        
    예시 응답:
        {
            "power": true,
            "current_channel": "EBC",
            "volume": 35,
            "message": "TV가 켜져 있으며 EBC 채널을 시청 중입니다. 볼륨은 35입니다.",
            "channel_info": {
                "name": "EBC",
                "description": "양질의 교육 콘텐츠를 제공하는 교육 방송 채널",
                "category": "교육"
            }
        }
    """
    logger.info("TV 상태 조회 요청 수신")
    result = await mock_api_request("/tv/status", "GET")
    return result

@mcp.tool()
async def set_tv_power(power_state: str) -> Dict[str, Any]:
    """
    TV 전원을 켜거나 끕니다.
    
    이 도구는 TV의 전원 상태를 제어합니다. TV가 꺼져 있을 때 켜거나,
    켜져 있을 때 끌 수 있습니다.
    
    Args:
        power_state (str): "on" 또는 "off" 값만 허용됩니다.
            - "on": TV 전원을 켭니다. 이전에 시청하던 채널이 표시됩니다.
            - "off": TV 전원을 끕니다. 화면이 꺼지고 모든 출력이 중단됩니다.
        
    Returns:
        Dict[str, Any]: TV 전원 제어 결과를 포함하는 딕셔너리 형태의 응답
            - result: 작업 결과 상태 ("success", "error" 등)
            - message: 결과 설명 메시지
    
    예시:
        set_tv_power("on") -> TV 전원을 켭니다.
        set_tv_power("off") -> TV 전원을 끕니다.
    """
    logger.info(f"TV 전원 제어 요청 수신: {power_state}")
    if power_state not in ["on", "off"]:
        return {"error": "전원 상태는 'on' 또는 'off'여야 합니다."}
    
    result = await mock_api_request("/tv/power", "POST", {"power_state": power_state})
    return result

@mcp.tool()
async def change_tv_channel(channel: str) -> Dict[str, Any]:
    """
    TV 채널을 변경합니다.
    
    이 도구는 TV의 현재 채널을 지정된 채널로 변경합니다. 채널 변경은
    TV가 켜져 있는 상태에서만 가능합니다.
    
    Args:
        channel (str): 변경할 채널명 (예: "EBC", "MBB", "너튜브" 등)
            - 채널명은 대소문자를 구분합니다.
            - 존재하지 않는 채널을 지정하면 오류가 발생합니다.
            - 사용 가능한 채널 목록은 get_tv_channels() 도구로 확인할 수 있습니다.
        
    Returns:
        Dict[str, Any]: 채널 변경 결과를 포함하는 딕셔너리 형태의 응답
            - result: 작업 결과 상태 ("success", "error" 등)
            - message: 결과 설명 메시지
    
    참고:
        TV가 꺼져 있는 경우에는 채널을 변경할 수 없으며 오류가 반환됩니다.
        TV 전원을 먼저 켠 후에 채널을 변경해야 합니다.
    
    예시:
        change_tv_channel("EBC") -> TV 채널을 "EBC"로 변경합니다.
        change_tv_channel("너튜브") -> TV 채널을 "너튜브"로 변경합니다.
    """
    logger.info(f"TV 채널 변경 요청 수신: {channel}")
    result = await mock_api_request("/tv/channel", "POST", {"channel": channel})
    return result

@mcp.tool()
async def set_tv_volume(level: int) -> Dict[str, Any]:
    """
    TV 볼륨을 조절합니다.
    
    이 도구는 TV의 볼륨 레벨을 조정합니다. 볼륨은 0(음소거)부터 100(최대)까지의
    정수 값으로 설정할 수 있으며, TV가 켜져 있는 상태에서만 조절 가능합니다.
    
    Args:
        level (int): 볼륨 값 (0~100 사이의 정수)
            - 0: 음소거 (소리 없음)
            - 50: 중간 볼륨
            - 100: 최대 볼륨
        
    Returns:
        Dict[str, Any]: 볼륨 조절 결과를 포함하는 딕셔너리 형태의 응답
            - result: 작업 결과 상태 ("success", "error" 등)
            - message: 결과 설명 메시지
    
    참고:
        TV가 꺼져 있는 경우에는 볼륨을 조절할 수 없으며 오류가 반환됩니다.
        볼륨을 0으로 설정하는 것은 음소거와 기능적으로 동일합니다.
    
    예시:
        set_tv_volume(30) -> TV 볼륨을 30%로 설정합니다.
        set_tv_volume(0) -> TV 소리를 음소거합니다.
        set_tv_volume(80) -> TV 볼륨을 80%로 높게 설정합니다.
    """
    logger.info(f"TV 볼륨 조절 요청 수신: {level}")
    if not (0 <= level <= 100):
        return {"error": "볼륨 값은 0에서 100 사이여야 합니다."}
    
    result = await mock_api_request("/tv/volume", "POST", {"level": level})
    return result

@mcp.tool()
async def get_tv_channels() -> Dict[str, Any]:
    """
    TV 채널 목록을 조회합니다.
    
    이 도구는 현재 시청 가능한 모든 TV 채널의 목록을 반환합니다.
    각 채널에 대한 이름, 설명, 카테고리 등의 정보가 포함됩니다.
    
    Returns:
        Dict[str, Any]: TV 채널 목록을 포함하는 딕셔너리 형태의 응답
            - channels: 채널 정보 객체의 배열
            
    채널 정보 객체 구조:
        - name: 채널 이름 (예: "EBC", "MBB", "너튜브" 등)
        - description: 채널에 대한 설명
        - category: 채널 카테고리 (예: "예능", "교육", "뉴스" 등)
    
    응답 예시:
        {
            "channels": [
                {
                    "name": "MBB",
                    "description": "재미있고 스트레스 풀리는 예능 프로그램을 제공하는 예능 전문 채널",
                    "category": "예능"
                },
                {
                    "name": "EBC",
                    "description": "양질의 교육 콘텐츠를 제공하는 교육 방송 채널",
                    "category": "교육"
                },
                ...
            ]
        }
    
    참고:
        이 함수는 TV의 전원 상태와 관계없이 항상 사용 가능한 채널 목록을 반환합니다.
    """
    logger.info("TV 채널 목록 조회 요청 수신")
    result = await mock_api_request("/tv/channels", "GET")
    return result

if __name__ == "__main__":
    # 서버 시작 메시지 출력
    print("TV MCP 서버가 실행 중입니다...")
    
    # SSE 트랜스포트를 사용하여 MCP 서버 시작
    mcp.run(transport="sse") 