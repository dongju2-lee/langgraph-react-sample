from fastapi import APIRouter, HTTPException
from models.audio_models import (
    AudioPlayRequest, AudioVolumeRequest, AudioPlaylistRequest, AudioResultResponse,
    AudioPlaylistsResponse, AudioPlaylistSongsResponse, AudioPowerRequest
)
from services.audio_service import audio_service
from logging_config import setup_logger
from typing import Dict, Any

# 로거 설정
logger = setup_logger("audio_api")

router = APIRouter(prefix="/audio", tags=["Audio"], responses={404: {"description": "Not found"}})

@router.get("/status", response_model=Dict[str, Any])
async def get_status():
    """
    오디오 상태 조회
    
    - 요청 본문이 필요 없습니다.
    - 예시 요청: GET /audio/status
    - 현재 오디오의 재생 상태, 선택된 플레이리스트, 재생 중인 곡, 볼륨 등 전반적인 상태 정보를 조회합니다.
    - 응답에는 playing(재생 여부), current_song(현재 곡), volume(볼륨), current_playlist(현재 플레이리스트) 정보가 포함됩니다.
    """
    logger.info("API 호출: 오디오 상태 조회")
    try:
        return audio_service.get_status()
    except Exception as e:
        logger.exception("오디오 상태 조회 실패")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/power", response_model=AudioResultResponse)
async def set_power(req: AudioPowerRequest):
    """
    오디오 전원 켜기/끄기
    
    - power_state: "on" 또는 "off" (문자열)
    - 예시: { "power_state": "on" }
    - 오디오 시스템의 전원을 켜거나 끕니다.
    - 전원이 꺼지면 현재 재생 중인 음악도 자동으로 중지됩니다.
    """
    logger.info(f"API 호출: 오디오 전원 {req.power_state}")
    try:
        return audio_service.set_power(req)
    except Exception as e:
        logger.exception("오디오 전원 제어 실패")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/play", response_model=AudioResultResponse)
async def play_audio(req: AudioPlayRequest):
    """
    음악/플레이리스트/특정 곡 재생

    - playlist: 재생할 플레이리스트 이름 (예: "명상", "공부")
    - song: 재생할 곡 이름 (예: "잔잔음악", "백색소음")
    - 둘 중 하나만 지정해도 되며, 둘 다 지정하면 song이 우선합니다.
    - 예시1: { "playlist": "명상" }
    - 예시2: { "song": "잔잔음악" }
    - 지정한 곡이나 플레이리스트를 스피커에서 재생합니다.
    """
    logger.info(f"API 호출: 오디오 재생 {req.playlist or req.song}")
    try:
        return audio_service.play_audio(req)
    except Exception as e:
        logger.exception("오디오 재생 실패")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stop", response_model=AudioResultResponse)
async def stop_audio():
    """
    음악 정지

    - 요청 본문이 필요 없습니다.
    - 예시: {}
    - 현재 재생 중인 모든 음악을 정지합니다.
    """
    logger.info("API 호출: 오디오 정지")
    try:
        return audio_service.stop_audio()
    except Exception as e:
        logger.exception("오디오 정지 실패")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/volume", response_model=AudioResultResponse)
async def set_volume(req: AudioVolumeRequest):
    """
    오디오 볼륨 조절

    - level: 볼륨 값 (0~10 사이의 정수)
    - 예시: { "level": 7 }
    - 스피커의 볼륨을 지정한 값으로 설정합니다.
    """
    logger.info(f"API 호출: 오디오 볼륨 {req.level}")
    try:
        return audio_service.set_volume(req)
    except Exception as e:
        logger.exception("오디오 볼륨 조절 실패")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/playlist", response_model=AudioResultResponse)
async def set_playlist(req: AudioPlaylistRequest):
    """
    플레이리스트 선택

    - playlist: 플레이리스트 이름 (예: "명상", "신나는 음악", "공부")
    - 예시: { "playlist": "명상" }
    - 지정한 플레이리스트를 현재 재생목록으로 설정합니다(자동 재생되지 않음).
    """
    logger.info(f"API 호출: 오디오 플레이리스트 {req.playlist}")
    try:
        return audio_service.set_playlist(req)
    except Exception as e:
        logger.exception("오디오 플레이리스트 선택 실패")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/playlists", response_model=AudioPlaylistsResponse)
async def get_playlists():
    """
    가능한 플레이리스트 목록 조회
    
    - 요청 본문이 필요 없습니다.
    - 예시 요청: GET /audio/playlists
    - 사용 가능한 모든 플레이리스트 목록을 반환합니다.
    - 각 플레이리스트는 이름, 설명, 카테고리 정보를 포함합니다.
    - 제공 플레이리스트: 명상(힐링), 신나는 음악(댄스/팝), 공부(집중) 등
    """
    logger.info("API 호출: 오디오 플레이리스트 목록 조회")
    try:
        return audio_service.get_playlists()
    except Exception as e:
        logger.exception("오디오 플레이리스트 목록 조회 실패")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/playlists/{playlist_name}/songs", response_model=AudioPlaylistSongsResponse)
async def get_playlist_songs(playlist_name: str):
    """
    플레이리스트 내 곡 목록 조회
    
    - playlist_name: 조회할 플레이리스트 이름 (예: "명상", "신나는 음악", "공부")
    - 예시 요청: GET /audio/playlists/명상/songs
    - 지정한 플레이리스트에 포함된 모든 곡 목록을 반환합니다.
    - 각 곡은 제목과 재생 시간 정보를 포함합니다.
    - 예: 명상 플레이리스트에는 "잔잔음악", "바다 파도 소리" 등이 포함됩니다.
    """
    logger.info(f"API 호출: '{playlist_name}' 플레이리스트 곡 목록 조회")
    try:
        return audio_service.get_playlist_songs(playlist_name)
    except Exception as e:
        logger.exception(f"'{playlist_name}' 플레이리스트 곡 목록 조회 실패")
        raise HTTPException(status_code=500, detail=str(e)) 