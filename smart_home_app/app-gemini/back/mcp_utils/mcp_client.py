# cooking_agent/mcp_utils/mcp_client.py
import asyncio
import os
from typing import Dict, Any, Optional

from langchain_mcp_adapters.client import MultiServerMCPClient
# main.py에서 MCP_CONFIG를 직접 가져오거나, config.py를 통해 가져옵니다.
# 여기서는 main.py에서 로드된 설정을 사용한다고 가정하고,
# 실제 사용 시에는 main.py에서 초기화된 MCP_CONFIG를 주입받는 방식도 고려할 수 있습니다.
# 또는, 이 파일에서도 .env를 직접 로드하여 MCP_CONFIG를 구성할 수 있습니다.

# .env 로드 (mcp_client.py에서도 직접 설정을 읽을 수 있도록)
from dotenv import load_dotenv
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env') # cooking_agent/.env
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    print(f"경고 (mcp_client.py): .env 파일을 찾을 수 없습니다 ({dotenv_path}).")


from ..utils.logger import setup_logger # utils.logger.py 가정

logger = setup_logger(__name__)

class MCPClientManager:
    _instance: Optional[MultiServerMCPClient] = None
    _lock = asyncio.Lock() # 비동기 초기화 시 동시성 문제 방지

    def __init__(self):
        # 이 클래스는 인스턴스화되어서는 안 됩니다.
        raise RuntimeError("MCPClientManager는 직접 인스턴스화할 수 없습니다. get_client()를 사용하세요.")

    @classmethod
    async def _get_mcp_config(cls) -> Dict[str, Dict[str, str]]:
        """MCP 설정을 .env 파일 또는 환경 변수에서 로드합니다."""
        # main.py와 동일한 방식으로 MCP_CONFIG 구성
        # 또는 main.py에서 생성된 MCP_CONFIG를 어떤 방식으로든 접근할 수 있어야 합니다.
        # 여기서는 .env를 직접 읽어 구성하는 예시를 보여드립니다.
        mcp_base_url = os.environ.get("MCP_BASE_URL", "http://localhost")
        config = {
            "refrigerator": {
                "url": f"{mcp_base_url}:{os.environ.get('REFRIGERATOR_MCP_PORT', '8001')}/sse",
                "transport": "sse",
            },
            "induction": {
                "url": f"{mcp_base_url}:{os.environ.get('INDUCTION_MCP_PORT', '8002')}/sse",
                "transport": "sse",
            },
            "microwave": {
                "url": f"{mcp_base_url}:{os.environ.get('MICROWAVE_MCP_PORT', '8003')}/sse",
                "transport": "sse",
            },
            "mobile": {
                "url": f"{mcp_base_url}:{os.environ.get('MOBILE_MCP_PORT', '8004')}/sse",
                "transport": "sse",
            },
            "cooking": {
                "url": f"{mcp_base_url}:{os.environ.get('COOKING_MCP_PORT', '8005')}/sse",
                "transport": "sse",
            },
            "personalization": {
                "url": f"{mcp_base_url}:{os.environ.get('PERSONALIZATION_MCP_PORT', '8006')}/sse",
                "transport": "sse",
            },
        }
        logger.debug(f"MCP 설정 로드 (mcp_client.py): {config}")
        return config

    @classmethod
    async def get_client(cls) -> MultiServerMCPClient:
        """
        MultiServerMCPClient의 싱글톤 인스턴스를 반환합니다.
        필요한 경우 비동기적으로 초기화합니다.
        """
        if cls._instance is None:
            async with cls._lock:
                if cls._instance is None: # 더블 체크 락킹
                    logger.info("MultiServerMCPClient 초기화 시작...")
                    try:
                        mcp_config = await cls._get_mcp_config()
                        client = MultiServerMCPClient(mcp_config)
                        # 클라이언트 연결 (필요한 경우 __aenter__ 호출)
                        # langchain-mcp-adapters는 일반적으로 첫 호출 시 연결을 시도하므로,
                        # 명시적인 __aenter__ 호출이 항상 필요한 것은 아닐 수 있습니다.
                        # 하지만, 애플리케이션 시작 시 연결을 확인하고 싶다면 호출할 수 있습니다.
                        # await client.__aenter__() # 필요시 주석 해제
                        cls._instance = client
                        logger.info("MultiServerMCPClient 초기화 및 (잠재적) 연결 완료.")
                    except Exception as e:
                        logger.error(f"MultiServerMCPClient 초기화 중 오류 발생: {e}", exc_info=True)
                        raise  # 초기화 실패 시 애플리케이션이 시작되지 않도록 예외 발생
        return cls._instance

    @classmethod
    async def close_client(cls):
        """
        MultiServerMCPClient 연결을 종료합니다. (애플리케이션 종료 시 호출)
        """
        if cls._instance:
            async with cls._lock:
                if cls._instance:
                    logger.info("MultiServerMCPClient 연결 종료 시도...")
                    try:
                        await cls._instance.__aexit__(None, None, None)
                        logger.info("MultiServerMCPClient 연결 종료 완료.")
                    except Exception as e:
                        logger.error(f"MultiServerMCPClient 연결 종료 중 오류 발생: {e}", exc_info=True)
                    finally:
                        cls._instance = None


async def call_mcp_tool(
    mcp_server_name: str,
    tool_name: str,
    tool_args: Optional[Dict[str, Any]] = None
) -> Any:
    """
    지정된 MCP 서버의 도구를 호출하고 결과를 반환합니다.

    Args:
        mcp_server_name (str): 호출할 MCP 서버의 이름 (예: "refrigerator", "induction").
                                MCP_CONFIG의 키와 일치해야 합니다.
        tool_name (str): 호출할 도구의 이름.
        tool_args (Optional[Dict[str, Any]]): 도구에 전달할 인자. Defaults to None.

    Returns:
        Any: 도구 호출 결과.

    Raises:
        ValueError: 유효하지 않은 MCP 서버 이름 또는 도구 이름이 제공된 경우.
        Exception: MCP 도구 호출 중 오류 발생 시.
    """
    if tool_args is None:
        tool_args = {}

    logger.info(f"MCP 도구 호출 요청: 서버='{mcp_server_name}', 도구='{tool_name}', 인자='{tool_args}'")

    try:
        client = await MCPClientManager.get_client()
        
        # langchain-mcp-adapters v0.0.6 이상에서는 client.call_tool 사용
        # 이전 버전에서는 client.servers[mcp_server_name].call_tool 등을 사용해야 할 수 있음
        # 여기서는 최신 API를 가정합니다.
        if not hasattr(client, 'call_tool'):
            # 이전 버전 호환성 또는 다른 API 사용 로직 (필요시)
            # 예: server_client = client.servers.get(mcp_server_name)
            # if not server_client:
            #     raise ValueError(f"'{mcp_server_name}' MCP 서버를 찾을 수 없습니다.")
            # result = await server_client.call_tool(tool_name, **tool_args)
            raise NotImplementedError("MultiServerMCPClient에 'call_tool' 메소드가 없습니다. langchain-mcp-adapters 버전을 확인하세요.")

        result = await client.call_tool(
            server_name=mcp_server_name,
            tool_name=tool_name,
            input_args=tool_args # input_args 파라미터 명칭 확인 필요 (라이브러리 버전에 따라 다를 수 있음)
                                 # langchain_mcp_adapters의 MultiServerMCPClient.call_tool 시그니처 확인
                                 # 보통은 **tool_args 또는 tool_input=tool_args 형태일 수 있음
                                 # langchain_mcp_adapters v0.0.6 기준으로는 server_name, tool_name, input_args가 맞음
        )
        logger.info(f"MCP 도구 호출 성공: 서버='{mcp_server_name}', 도구='{tool_name}', 결과='{str(result)[:200]}...'") # 결과가 길 수 있으므로 일부만 로깅
        return result
    except ValueError as ve: # 서버/도구 이름 오류 등
        logger.error(f"MCP 도구 호출 값 오류: {ve}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"MCP 도구 '{mcp_server_name}.{tool_name}' 호출 중 예기치 않은 오류 발생: {e}", exc_info=True)
        raise # 예외를 다시 발생시켜 호출한 노드에서 처리하도록 함

# 애플리케이션 종료 시 호출될 수 있도록 함수 제공
async def shutdown_mcp_client():
    await MCPClientManager.close_client()


# 간단한 테스트용 코드 (이 파일을 직접 실행할 때)
if __name__ == "__main__":
    async def main_test():
        # 로깅 설정 (main.py와 유사하게)
        import logging as py_logging # 충돌 방지
        py_logging.basicConfig(level=os.environ.get("LOG_LEVEL", "DEBUG").upper(), format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        logger.info("MCP 클라이언트 테스트 시작...")
        try:
            # 예시: 냉장고 내용물 가져오기 (실제 MCP 서버가 실행 중이어야 함)
            # refrigerator_content = await call_mcp_tool(
            #     mcp_server_name="refrigerator",
            #     tool_name="get_contents" # 실제 도구 이름으로 변경
            # )
            # logger.info(f"테스트 - 냉장고 내용물: {refrigerator_content}")

            # 예시: 인덕션 상태 가져오기
            # induction_status = await call_mcp_tool(
            #     mcp_server_name="induction",
            #     tool_name="get_status" # 실제 도구 이름으로 변경
            # )
            # logger.info(f"테스트 - 인덕션 상태: {induction_status}")

            logger.info("MCP 클라이언트 테스트 (호출 예시는 주석 처리됨, 실제 테스트 시 주석 해제 및 도구 이름 확인 필요)")

        except Exception as e:
            logger.error(f"MCP 클라이언트 테스트 중 오류 발생: {e}")
        finally:
            await shutdown_mcp_client() # 테스트 후 클라이언트 종료
            logger.info("MCP 클라이언트 테스트 종료.")

    asyncio.run(main_test())
