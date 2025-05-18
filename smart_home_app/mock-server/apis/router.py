from fastapi import APIRouter
from apis import refrigerator, microwave, induction, personalization, cooking, mobile
from apis import tv, light, curtain, audio
from logging_config import setup_logger

# API 라우터용 로거 설정
logger = setup_logger("api_router")

# 메인 라우터
router = APIRouter()

logger.info("Initializing API routers")
router.include_router(refrigerator.router)
logger.info("Refrigerator router initialized")
router.include_router(microwave.router)
logger.info("Microwave router initialized")
router.include_router(induction.router)
logger.info("Induction router initialized")
router.include_router(personalization.router)
logger.info("Personalization router initialized")
router.include_router(cooking.router)
logger.info("Cooking router initialized")
router.include_router(mobile.router)
logger.info("Mobile router initialized")
router.include_router(tv.router)
logger.info("TV router initialized")
router.include_router(light.router)
logger.info("Light router initialized")
router.include_router(curtain.router)
logger.info("Curtain router initialized")
router.include_router(audio.router)
logger.info("Audio router initialized")
