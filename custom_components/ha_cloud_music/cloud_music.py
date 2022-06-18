import requests, uuid, time, json

class CloudMusic():

    def __init__(self, hass) -> None:
        self.hass = hass
        self.api_url = 'http://music.frps.jiluxinqing.com'
        self._playindex = 0
        self._playlist = []
    
    @property
    def playlist(self):
        return self._playlist

    # 加载播放列表
    def load_playlist(self, playlist):
        self._playlist = playlist

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