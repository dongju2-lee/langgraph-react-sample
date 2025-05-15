from typing import List, Any, Tuple, Optional

class PlanExecuteState(dict):
    input: str
    plan: List[str]
    current_step: int
    past_steps: List[Tuple[str, str]]
    response: Optional[str]
    messages: List[Any]
