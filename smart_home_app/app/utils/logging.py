from loguru import logger
import os

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

def get_logger(session_id: str = None):
    """
    세션별 로그 파일을 생성하고 logger를 반환합니다.
    session_id가 없으면 smart_home.log에 기록합니다.
    """
    if session_id:
        log_path = os.path.join(LOG_DIR, f"session_{session_id}.log")
    else:
        log_path = os.path.join(LOG_DIR, "smart_home.log")
    logger.add(log_path, rotation="10 MB", retention="10 days", enqueue=True, backtrace=True, diagnose=True)
    return logger

# 사용 예시:
# log = get_logger(session_id)
# log.info("로그 메시지")
