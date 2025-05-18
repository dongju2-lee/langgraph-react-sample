from models.audio_models import (
    AudioPlayRequest, AudioVolumeRequest, AudioPlaylistRequest, AudioResultResponse,
    AudioPlaylist, AudioPlaylistsResponse, AudioSong, AudioPlaylistSongsResponse
)
from logging_config import setup_logger

logger = setup_logger("audio_service")

# 샘플 플레이리스트 데이터
AUDIO_PLAYLISTS = [
    AudioPlaylist(
        name="명상",
        description="마음의 안정을 찾는 데 도움이 되는 잔잔한 음악 모음",
        category="힐링"
    ),
    AudioPlaylist(
        name="신나는 음악",
        description="기분을 업시키고 활력을 불어넣는 신나는 음악 모음",
        category="댄스/팝"
    ),
    AudioPlaylist(
        name="공부",
        description="집중력을 높이고 학습 효율을 높여주는 음악 모음",
        category="집중"
    )
]

# 샘플 플레이리스트별 곡 데이터
PLAYLIST_SONGS = {
    "명상": [
        AudioSong(title="잔잔음악", duration="5:30"),
        AudioSong(title="바다 파도 소리", duration="10:00"),
        AudioSong(title="새소리와 함께하는 명상", duration="8:45")
    ],
    "신나는 음악": [
        AudioSong(title="슈퍼노바", duration="3:45"),
        AudioSong(title="강남스타일", duration="4:12"),
        AudioSong(title="다이너마이트", duration="3:20")
    ],
    "공부": [
        AudioSong(title="숲속의소리", duration="12:00"),
        AudioSong(title="백색소음", duration="60:00"),
        AudioSong(title="집중을 위한 피아노", duration="15:30")
    ]
}

class AudioService:
    def play_audio(self, req: AudioPlayRequest) -> AudioResultResponse:
        logger.info(f"오디오 재생: {req.playlist or req.song}")
        if req.song:
            return AudioResultResponse(result="success", message=f"{req.song} 재생 중")
        elif req.playlist:
            return AudioResultResponse(result="success", message=f"{req.playlist} 플레이리스트 재생 중")
        else:
            return AudioResultResponse(result="success", message="기본 오디오 재생 중")

    def stop_audio(self) -> AudioResultResponse:
        logger.info("오디오 정지")
        return AudioResultResponse(result="success", message="오디오 정지됨")

    def set_volume(self, req: AudioVolumeRequest) -> AudioResultResponse:
        logger.info(f"오디오 볼륨 조절: {req.level}")
        return AudioResultResponse(result="success", message=f"오디오 볼륨이 {req.level}으로 변경됨")

    def set_playlist(self, req: AudioPlaylistRequest) -> AudioResultResponse:
        logger.info(f"오디오 플레이리스트 선택: {req.playlist}")
        return AudioResultResponse(result="success", message=f"{req.playlist} 플레이리스트 선택됨")
    
    def get_playlists(self) -> AudioPlaylistsResponse:
        logger.info("플레이리스트 목록 조회")
        return AudioPlaylistsResponse(playlists=AUDIO_PLAYLISTS)
    
    def get_playlist_songs(self, playlist_name: str) -> AudioPlaylistSongsResponse:
        logger.info(f"플레이리스트 '{playlist_name}' 곡 목록 조회")
        
        if playlist_name not in PLAYLIST_SONGS:
            # 기본값 - 실제로는 예외를 발생시키는 것이 좋습니다
            return AudioPlaylistSongsResponse(
                playlist_name=playlist_name,
                songs=[]
            )
            
        return AudioPlaylistSongsResponse(
            playlist_name=playlist_name,
            songs=PLAYLIST_SONGS[playlist_name]
        )

audio_service = AudioService() 