import uuid
from typing import Dict, Any

# 인메모리 세션 저장소
db: Dict[str, Any] = {}

def create_session() -> str:
    """새로운 세션 ID를 생성하고 초기화합니다."""
    session_id = str(uuid.uuid4())
    db[session_id] = {}
    return session_id

def get_session(session_id: str) -> dict:
    """세션 ID로 상태를 조회합니다."""
    return db.get(session_id, {})

def set_session(session_id: str, state: dict):
    """세션 ID에 상태를 저장합니다."""
    db[session_id] = state
