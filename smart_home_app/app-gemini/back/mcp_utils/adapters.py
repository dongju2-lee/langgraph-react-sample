import os
from dotenv import load_dotenv
import httpx # HTTP 요청을 위한 라이브러리, requirements.txt에 추가 필요

load_dotenv()

# MCP 서버 URL 환경 변수 이름과 기본값
MCP_URL_ENV_VARS = {
    "refrigerator": "REFRIGERATOR_MCP_URL",
    "induction": "INDUCTION_MCP_URL",
    "microwave": "MICROWAVE_MCP_URL",
    "mobile": "MOBILE_MCP_URL",
    "cooking": "COOKING_MCP_URL",
    "personalization": "PERSONALIZATION_MCP_URL",
}

class BaseMCPAdapter:
    def __init__(self, mcp_type: str, base_url: str):
        self.mcp_type = mcp_type
        self.base_url = base_url
        if not self.base_url:
            raise ValueError(f"{mcp_type} MCP URL이 설정되지 않았습니다.")

    async def _request(self, method: str, endpoint: str, params: dict = None, data: dict = None) -> dict:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.request(method, f"{self.base_url}{endpoint}", params=params, json=data)
                response.raise_for_status() # 오류 발생 시 예외 처리
                return response.json()
            except httpx.HTTPStatusError as e:
                # 실제로는 로깅 등을 통해 더 자세한 오류 처리 필요
                print(f"{self.mcp_type} MCP 요청 오류: {e.response.status_code} - {e.response.text}")
                raise
            except httpx.RequestError as e:
                print(f"{self.mcp_type} MCP 연결 오류: {e}")
                raise

    async def get_status(self) -> dict:
        """MCP 서버의 기본 상태를 조회합니다."""
        return await self._request("GET", "/status")

# --- 개별 MCP 어댑터 클래스 정의 --- #

class RefrigeratorMCPAdapter(BaseMCPAdapter):
    def __init__(self):
        url = os.getenv(MCP_URL_ENV_VARS["refrigerator"])
        super().__init__("refrigerator", url)

    async def get_contents(self) -> dict:
        """냉장고 내용물 조회"""
        return await self._request("GET", "/contents")

    async def check_ingredient(self, ingredient_name: str) -> dict:
        """특정 식재료 확인"""
        return await self._request("GET", "/check_ingredient", params={"name": ingredient_name})

class InductionMCPAdapter(BaseMCPAdapter):
    def __init__(self):
        url = os.getenv(MCP_URL_ENV_VARS["induction"])
        super().__init__("induction", url)

    async def turn_on(self) -> dict:
        return await self._request("POST", "/turn_on")

    async def turn_off(self) -> dict:
        return await self._request("POST", "/turn_off")

    async def set_power(self, level: int) -> dict: # 1 ~ 10 등
        return await self._request("POST", "/set_power", data={"level": level})

    async def set_timer(self, minutes: int) -> dict:
        return await self._request("POST", "/set_timer", data={"minutes": minutes})
    
    async def get_state(self) -> dict:
        """인덕션 현재 상태 (켜짐/꺼짐, 온도, 남은 시간 등) 조회"""
        return await self._request("GET", "/state")

class MicrowaveMCPAdapter(BaseMCPAdapter):
    def __init__(self):
        url = os.getenv(MCP_URL_ENV_VARS["microwave"])
        super().__init__("microwave", url)

    async def start(self, seconds: int, power_level: str = "high") -> dict:
        return await self._request("POST", "/start", data={"seconds": seconds, "power_level": power_level})

    async def stop(self) -> dict:
        return await self._request("POST", "/stop")

    async def get_state(self) -> dict:
        """전자레인지 현재 상태 조회"""
        return await self._request("GET", "/state")

class MobileMCPAdapter(BaseMCPAdapter):
    def __init__(self):
        url = os.getenv(MCP_URL_ENV_VARS["mobile"])
        super().__init__("mobile", url)

    async def send_message(self, recipient: str, message: str) -> dict:
        return await self._request("POST", "/send_message", data={"recipient": recipient, "message": message})

class CookingMCPAdapter(BaseMCPAdapter):
    def __init__(self):
        url = os.getenv(MCP_URL_ENV_VARS["cooking"])
        super().__init__("cooking", url)

    async def search_recipes(self, query: Optional[str] = None, ingredients: Optional[list[str]] = None) -> dict:
        params = {}
        if query: params["query"] = query
        if ingredients: params["ingredients"] = ",".join(ingredients) # 쉼표로 구분된 문자열로 전달 가정
        return await self._request("GET", "/search_recipes", params=params)

    async def get_recipe_details(self, recipe_id: str) -> dict:
        return await self._request("GET", f"/recipes/{recipe_id}") # 엔드포인트 예시

    async def get_substitute_ingredient(self, original_ingredient: str, available_ingredients: Optional[list[str]] = None) -> dict:
        params = {"original_ingredient": original_ingredient}
        if available_ingredients: params["available_ingredients"] = ",".join(available_ingredients)
        return await self._request("GET", "/substitute_ingredient", params=params)

# MCP 클라이언트 인스턴스를 생성하고 상태에 저장하기 위한 헬퍼 함수
async def get_mcp_clients() -> dict:
    # 실제 langchain-mcp-adapters 라이브러리가 있다면 해당 방식으로 클라이언트 초기화
    # 여기서는 위에서 정의한 어댑터 클래스를 직접 사용합니다.
    clients = {}
    try: clients["refrigerator"] = RefrigeratorMCPAdapter()
    except ValueError: clients["refrigerator"] = None
    try: clients["induction"] = InductionMCPAdapter()
    except ValueError: clients["induction"] = None
    try: clients["microwave"] = MicrowaveMCPAdapter()
    except ValueError: clients["microwave"] = None
    try: clients["mobile"] = MobileMCPAdapter()
    except ValueError: clients["mobile"] = None
    try: clients["cooking"] = CookingMCPAdapter()
    except ValueError: clients["cooking"] = None
    # personalization_url = os.getenv(MCP_URL_ENV_VARS["personalization"])
    # if personalization_url: # 선택 사항이므로 URL이 있을 때만 초기화
    #     clients["personalization"] = PersonalizationMCPAdapter()
    # else:
    #     clients["personalization"] = None
    return clients 