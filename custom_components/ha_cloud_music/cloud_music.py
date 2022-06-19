import uuid, time, json
from .http_api import http_get
from .models.music_info import MusicInfo

class CloudMusic():

    def __init__(self, hass, url) -> None:
        self.hass = hass
        self.api_url = url.strip('/')
        self._playindex = 0
        self._playlist = []
        self.cookie = {}
    
    @property
    def playlist(self) -> list[MusicInfo]:
        return self._playlist

    # 加载播放列表
    async def async_load_playlist(self, id, playindex=0):
        res = await http_get(self.api_url + '/playlist/track/all?id=' + str(id), self.cookie)
        def format_playlist(item):
            id = item['id']
            song = item['name']
            singer = item['ar'][0]['name']
            album = item['al']['name'] 
            duration = item['dt']
            url = ''
            picUrl = item['picUrl'] + '?param=500y500'
            return MusicInfo(id, song, singer, album, duration, url, picUrl)
        
        self._playlist = list(map(format_playlist, res['songs']))
        self._playindex = playindex

    # 获取播放链接
    def get_url(self):
        pass

    # 下一曲
    def next(self):
        count = len(self._playlist)
        if count <= 1:
            return
        self._playindex = self._playindex + 1
        if self._playindex == count:
            self._playindex = 0

    # 上一曲
    def previous(self):
        count = len(self._playlist)
        if count <= 1:
            return
        self._playindex = self._playindex - 1
        if self._playindex < 0:
            self._playindex = count - 1