from typing_extensions import TypedDict, Annotated
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages

# 메시지 기반 state (메인/서브그래프 모두에서 사용)
class SmartHomeState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    system_mode: str  # "normal" 또는 "cooking"
    # 필요시 추가 필드 (예: 레시피, 단계 등)
    recipe: dict | None
    current_step: int | None
