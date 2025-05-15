# cooking_agent/state.py
from typing import TypedDict, List, Dict, Any, Literal, Optional
from langchain_core.messages import BaseMessage

# --- MCP 서버 클라이언트/어댑터 타입을 위한 플레이스홀더 ---
# 실제 MCP 클라이언트 라이브러리가 있다면 해당 타입을 사용합니다.
# 예시: from mcp_adapters import RefrigeratorClient, InductionClient 등
class BaseMCPClient:
    async def execute(self, action: str, params: Dict[str, Any]) -> Any:
        raise NotImplementedError


class RefrigeratorClient(BaseMCPClient):
    pass  # 실제 구현 필요


class InductionClient(BaseMCPClient):
    pass  # 실제 구현 필요


class MicrowaveClient(BaseMCPClient):
    pass  # 실제 구현 필요


class MobileClient(BaseMCPClient):
    pass  # 실제 구현 필요


class CookingMCPClient(BaseMCPClient):
    pass  # 실제 구현 필요


class PersonalizationClient(BaseMCPClient):
    pass  # 실제 구현 필요


class MCPClients(TypedDict):
    refrigerator: Optional[RefrigeratorClient]
    induction: Optional[InductionClient]
    microwave: Optional[MicrowaveClient]
    mobile: Optional[MobileClient]
    cooking: Optional[CookingMCPClient]
    personalization: Optional[PersonalizationClient]


class ToolCall(TypedDict):
    tool_name: str  # 예: "refrigerator.get_contents" 또는 "induction.set_power"
    tool_args: Dict[str, Any]
    # mcp_server_name: str # MCPClients 구조를 사용하므로 직접 지정보다 타입으로 구분
    mcp_client_type: Literal[
        "refrigerator", "induction", "microwave", "mobile", "cooking", "personalization"
    ]


class Recipe(TypedDict):
    id: str
    name: str
    description: Optional[str]
    ingredients: List[str]
    steps: List[Dict[str, Any]]  # 각 단계는 지침, 필요 MCP 등을 포함
    estimated_time_minutes: Optional[int]
    difficulty: Optional[str]


class AgentState(TypedDict):
    """LangGraph 에이전트의 상태"""

    # --- 입력 및 대화 관리 ---
    messages: List[BaseMessage]  # 전체 대화 기록

    # --- 의도 및 모드 관리 ---
    current_intent: Optional[
        Literal[
            "general_chat",
            "query_device_status",  # "지금 인덕션 켜져있어?"
            "direct_device_control",  # "인덕션 꺼줘"
            "recipe_recommendation_ingredient",  # "이 재료로 만들만한 레시피 추천해줘"
            "recipe_recommendation_general",  # "파스타 레시피 추천해줘"
            "recipe_selection",  # 사용자가 레시피 선택
            "start_cooking",  # "요리 시작할까요?" -> "응"
            "next_cooking_step",  # 다음 요리 단계 진행
            "ingredient_check_needed",  # 현재 단계 재료 확인 필요
            "ingredient_missing_action",  # 재료 없을 때 사용자에게 문의
            "substitute_ingredient_search",  # 대체 재료 탐색
            "execute_tool_call",  # MCP 도구 실행
            "inform_user",  # 사용자에게 정보 전달 (예: "고구마가 없습니다")
            "ask_user_confirmation", # 사용자에게 확인 요청 (예: "감자로 대체할까요?")
            "cooking_complete", # 요리 완료
            "send_message_request", # "엄마에게 메시지 보내줘"
            "other"
        ]
    ]
    active_flow: Optional[Literal["cooking", "none"]] # 현재 진행중인 주요 흐름

    # --- 쿠킹 플로우 관련 상태 ---
    # 사용자의 원래 레시피 요청 (예: "토마토 스파게티", "냉장고 재료로 만들 수 있는 요리")
    recipe_query_input: Optional[str]
    available_recipes: Optional[List[Recipe]] # 추천된 레시피 목록
    selected_recipe: Optional[Recipe] # 사용자가 선택한 레시피
    current_cooking_step_index: Optional[int] # 현재 진행중인 요리 단계 (0부터 시작)
    current_step_details: Optional[Dict[str, Any]] # 현재 단계 지침, 필요한 MCP 정보 등

    # --- 식재료 관리 ---
    # 사용자가 명시한 사용 가능 재료 또는 냉장고에서 가져온 재료
    user_provided_ingredients: Optional[List[str]]
    # 현재 단계에 필요한 특정 재료들
    required_ingredients_for_current_step: Optional[List[str]]
    # 냉장고 등에서 확인된 현재 보유 재료 (이름: 수량/정보)
    inventory: Optional[Dict[str, Any]]
    missing_ingredients: Optional[List[str]] # 현재 단계에 부족한 재료
    # 대체 재료 제안 (예: {"original": "고구마", "substitute": "감자"})
    alternative_ingredient_suggestion: Optional[Dict[str, str]]

    # --- MCP 및 장치 제어 관련 상태 ---
    # 실행해야 할 MCP 호출 목록 (실제 호출 전 상태)
    pending_tool_calls: Optional[List[ToolCall]]
    # 최근 MCP 호출 결과 (여러 개일 수 있음)
    tool_call_results: Optional[List[Dict[str, Any]]]
    # 연결된 MCP 클라이언트 인스턴스
    mcp_clients: Optional[MCPClients]

    # --- 사용자에게 전달할 메시지 ---
    # 에이전트가 사용자에게 다음에 할 말
    response_to_user: Optional[str]

    # --- 다음 액션 결정 (라우팅에 사용) ---
    # 특정 노드로 강제 이동시키고 싶을 때 사용
    next_node_override: Optional[str]

    # --- 디버깅/오류 정보 ---
    error_message: Optional[str]
    debug_info: Optional[Dict[str, Any]]
