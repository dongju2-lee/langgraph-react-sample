from pydantic import BaseModel
from typing import Optional, List

class AudioPowerRequest(BaseModel):
    power_state: str  # "on" 또는 "off"

class AudioPlayRequest(BaseModel):
    playlist: Optional[str] = None
    song: Optional[str] = None

class AudioVolumeRequest(BaseModel):
    level: int

class AudioPlaylistRequest(BaseModel):
    playlist: str

class AudioResultResponse(BaseModel):
    result: str
    message: str
    
class AudioSong(BaseModel):
    title: str
    duration: Optional[str] = None
    
class AudioPlaylist(BaseModel):
    name: str
    description: str
    category: str
    
class AudioPlaylistsResponse(BaseModel):
    playlists: List[AudioPlaylist]
    
class AudioPlaylistSongsResponse(BaseModel):
    playlist_name: str
    songs: List[AudioSong] 