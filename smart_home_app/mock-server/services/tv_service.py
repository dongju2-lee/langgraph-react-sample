from models.tv_models import (
    TVPowerRequest, TVChannelRequest, TVVolumeRequest, 
    TVResultResponse, TVChannel, TVChannelsResponse
)
from logging_config import setup_logger

logger = setup_logger("tv_service")

# 샘플 채널 데이터
TV_CHANNELS = [
    TVChannel(
        name="MBB",
        description="재미있고 스트레스 풀리는 예능 프로그램을 제공하는 예능 전문 채널",
        category="예능"
    ),
    TVChannel(
        name="EBC",
        description="양질의 교육 콘텐츠를 제공하는 교육 방송 채널",
        category="교육"
    ),
    TVChannel(
        name="LOTTI-HOMESHOPPING",
        description="다양한 상품을 구매할 수 있는 홈쇼핑 채널",
        category="쇼핑"
    ),
    TVChannel(
        name="NEWS24",
        description="24시간 뉴스를 제공하는 뉴스 전문 채널",
        category="뉴스"
    ),
    TVChannel(
        name="MOVIE-WORLD",
        description="최신 영화와 클래식 명작을 방영하는 영화 전문 채널",
        category="영화"
    ),
    TVChannel(
        name="KIDS-LAND",
        description="어린이를 위한 교육적이고 재미있는 프로그램을 제공하는 키즈 채널",
        category="어린이"
    ),
    TVChannel(
        name="DOCU-PLUS",
        description="자연, 역사, 과학 등 다양한 주제의 다큐멘터리를 방영하는 채널",
        category="다큐멘터리"
    ),
    TVChannel(
        name="너튜브",
        description="재미있는 영상과 스포츠 중계를 볼 수 있는 인기 영상 스트리밍 채널",
        category="영상/스포츠"
    )
]

class TVService:
    def set_power(self, req: TVPowerRequest) -> TVResultResponse:
        logger.info(f"TV 전원 제어: {req.power_state}")
        return TVResultResponse(result="success", message=f"TV 전원이 {req.power_state} 상태로 변경됨")

    def set_channel(self, req: TVChannelRequest) -> TVResultResponse:
        logger.info(f"TV 채널 변경: {req.channel}")
        return TVResultResponse(result="success", message=f"TV 채널이 {req.channel}로 변경됨")

    def set_volume(self, req: TVVolumeRequest) -> TVResultResponse:
        logger.info(f"TV 볼륨 조절: {req.level}")
        return TVResultResponse(result="success", message=f"TV 볼륨이 {req.level}으로 변경됨")
    
    def get_channels(self) -> TVChannelsResponse:
        logger.info("TV 채널 목록 조회")
        return TVChannelsResponse(channels=TV_CHANNELS)

tv_service = TVService() 