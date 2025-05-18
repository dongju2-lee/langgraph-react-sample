from models.audio_models import (
    AudioPlayRequest, AudioVolumeRequest, AudioPlaylistRequest, AudioResultResponse,
    AudioPlaylist, AudioPlaylistsResponse, AudioSong, AudioPlaylistSongsResponse,
    AudioPowerRequest
)
from logging_config import setup_logger
from typing import Dict, Any, Optional, List

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

# 오디오 상태 저장용 전역 변수
audio_state = {
    "power_state": "off",  # "on" 또는 "off"
    "playing": False,  # 재생 중 여부
    "volume": 5,  # 볼륨 (0-10)
    "current_playlist": None,  # 현재 선택된 플레이리스트
    "current_song": None,  # 현재 재생 중인 곡
}

class AudioService:
    def get_status(self) -> Dict[str, Any]:
        """
        오디오 상태 정보 조회
        """
        logger.info("오디오 상태 조회")
        
        # 현재 플레이리스트 정보 찾기
        current_playlist_info = None
        if audio_state["current_playlist"]:
            current_playlist_info = next(
                (p.dict() for p in AUDIO_PLAYLISTS if p.name == audio_state["current_playlist"]),
                None
            )
        
        # 현재 곡 정보 찾기
        current_song_info = None
        if audio_state["current_song"] and audio_state["current_playlist"]:
            playlist_songs = PLAYLIST_SONGS.get(audio_state["current_playlist"], [])
            current_song_info = next(
                (song.dict() for song in playlist_songs if song.title == audio_state["current_song"]),
                None
            )
        
        return {
            "power": audio_state["power_state"] == "on",
            "playing": audio_state["playing"],
            "volume": audio_state["volume"],
            "current_playlist": audio_state["current_playlist"],
            "current_song": audio_state["current_song"],
            "playlist_info": current_playlist_info,
            "song_info": current_song_info,
            "message": self._get_status_message()
        }
        
    def _get_status_message(self) -> str:
        """상태 메시지 생성"""
        if audio_state["power_state"] == "off":
            return "오디오가 꺼져 있습니다."
            
        if audio_state["playing"] and audio_state["current_song"]:
            return f"현재 '{audio_state['current_playlist']}' 플레이리스트의 '{audio_state['current_song']}' 곡을 재생 중입니다. 볼륨: {audio_state['volume']}"
        elif not audio_state["playing"]:
            return f"오디오가 켜져 있지만 재생이 중지되었습니다. 선택된 플레이리스트: {audio_state['current_playlist'] or '없음'}"
        else:
            return f"오디오가 켜져 있고 플레이리스트 '{audio_state['current_playlist']}'가 선택되었지만 재생 중인 곡이 없습니다."
    
    def set_power(self, req: AudioPowerRequest) -> AudioResultResponse:
        """
        오디오 전원 켜기/끄기
        """
        logger.info(f"오디오 전원 제어: {req.power_state}")
        
        # 이미 같은 상태인 경우
        if audio_state["power_state"] == req.power_state:
            return AudioResultResponse(
                result="info", 
                message=f"오디오가 이미 {req.power_state} 상태입니다."
            )
        
        # 전원 상태 업데이트
        audio_state["power_state"] = req.power_state
        
        # 전원이 꺼지면 재생도 중지
        if req.power_state == "off":
            audio_state["playing"] = False
        
        return AudioResultResponse(
            result="success", 
            message=f"오디오 전원이 {req.power_state} 상태로 변경되었습니다."
        )
    
    def play_audio(self, req: AudioPlayRequest) -> AudioResultResponse:
        logger.info(f"오디오 재생: {req.playlist or req.song}")
        
        # 전원이 꺼져 있는 경우
        if audio_state["power_state"] == "off":
            # 전원 자동 켜기
            logger.info("오디오가 꺼져 있어 자동으로 켭니다.")
            audio_state["power_state"] = "on"
        
        # 상태 업데이트
        audio_state["playing"] = True
        
        if req.song:
            audio_state["current_song"] = req.song
            # 해당 곡이 속한 플레이리스트 찾기
            for playlist_name, songs in PLAYLIST_SONGS.items():
                if any(song.title == req.song for song in songs):
                    audio_state["current_playlist"] = playlist_name
                    break
            return AudioResultResponse(result="success", message=f"{req.song} 재생 중")
        elif req.playlist:
            audio_state["current_playlist"] = req.playlist
            # 플레이리스트의 첫 번째 곡을 재생
            if req.playlist in PLAYLIST_SONGS and PLAYLIST_SONGS[req.playlist]:
                audio_state["current_song"] = PLAYLIST_SONGS[req.playlist][0].title
            return AudioResultResponse(result="success", message=f"{req.playlist} 플레이리스트 재생 중")
        else:
            return AudioResultResponse(result="success", message="기본 오디오 재생 중")

    def stop_audio(self) -> AudioResultResponse:
        logger.info("오디오 정지")
        
        # 전원이 꺼져 있는 경우
        if audio_state["power_state"] == "off":
            return AudioResultResponse(result="error", message="오디오가 꺼져 있어 정지할 수 없습니다.")
        
        # 이미 정지되어 있는 경우
        if not audio_state["playing"]:
            return AudioResultResponse(result="info", message="오디오가 이미 정지되어 있습니다.")
        
        # 상태 업데이트
        audio_state["playing"] = False
        # 현재 곡은 그대로 유지 (정지 후 다시 재생 시 사용)
        
        return AudioResultResponse(result="success", message="오디오 정지됨")

    def set_volume(self, req: AudioVolumeRequest) -> AudioResultResponse:
        logger.info(f"오디오 볼륨 조절: {req.level}")
        
        # 전원이 꺼져 있는 경우
        if audio_state["power_state"] == "off":
            return AudioResultResponse(result="error", message="오디오가 꺼져 있어 볼륨을 조절할 수 없습니다.")
        
        # 볼륨 범위 확인
        if not (0 <= req.level <= 10):
            logger.warning(f"유효하지 않은 볼륨 레벨: {req.level}")
            return AudioResultResponse(result="error", message="볼륨 레벨은 0에서 10 사이여야 합니다.")
        
        # 상태 업데이트
        audio_state["volume"] = req.level
        
        return AudioResultResponse(result="success", message=f"오디오 볼륨이 {req.level}으로 변경됨")

    def set_playlist(self, req: AudioPlaylistRequest) -> AudioResultResponse:
        logger.info(f"오디오 플레이리스트 선택: {req.playlist}")
        
        # 전원이 꺼져 있는 경우
        if audio_state["power_state"] == "off":
            # 전원 자동 켜기
            logger.info("오디오가 꺼져 있어 자동으로 켭니다.")
            audio_state["power_state"] = "on"
        
        # 플레이리스트 존재 여부 확인
        playlist_exists = any(p.name == req.playlist for p in AUDIO_PLAYLISTS)
        if not playlist_exists:
            logger.warning(f"존재하지 않는 플레이리스트: {req.playlist}")
            return AudioResultResponse(result="error", message=f"플레이리스트 '{req.playlist}'가 존재하지 않습니다.")
        
        # 상태 업데이트
        audio_state["current_playlist"] = req.playlist
        # 현재 곡은 선택하지 않음 (플레이리스트만 선택)
        
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