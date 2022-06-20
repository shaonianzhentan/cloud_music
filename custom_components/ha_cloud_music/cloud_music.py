import uuid, time, json, os
from .http_api import http_get
from .models.music_info import MusicInfo, MusicSource
from homeassistant.helpers.storage import STORAGE_DIR
from homeassistant.util.json import load_json, save_json

class CloudMusic():

    def __init__(self, url) -> None:
        self.api_url = url.strip('/')
        self._playindex = 0
        self._playlist = []
        self.cookie = {}
        # 读取本地存储文件
        self.playlist_filepath = os.path.abspath(f'{STORAGE_DIR}/cloud_music.playlist')
        if os.path.exists(self.playlist_filepath):
            res = load_json(self.playlist_filepath)
            self._playindex = res['index']
            def format_playlist(item):
                return MusicInfo(item['id'], 
                    item['song'], 
                    item['singer'], 
                    item['album'], 
                    item['duration'], 
                    item['url'], 
                    item['picUrl'], 
                    item['source'])
            self._playlist = list(map(format_playlist, res['list']))
    
    @property
    def playindex(self):
        return self._playindex

    @property
    def playlist(self) -> list[MusicInfo]:
        return self._playlist

    # 加载播放列表
    async def async_load_playlist(self, playlist_id, playindex=0):
        res = await http_get(self.api_url + f'/playlist/track/all?id={playlist_id}', self.cookie)
        json_list = []
        def format_playlist(item):
            id = item['id']
            song = item['name']
            singer = item['ar'][0]['name']
            album = item['al']['name'] 
            duration = item['dt']
            url = ''
            picUrl = item['al'].get('picUrl', 'https://p2.music.126.net/fL9ORyu0e777lppGU3D89A==/109951167206009876.jpg') + '?param=500y500'
            
            json_list.append({
                'id': id, 
                'song': song, 
                'singer': singer, 
                'album': album, 
                'duration': duration, 
                'url': url, 
                'picUrl': picUrl,
                'source': MusicSource.PLAYLIST.value
            })
            return MusicInfo(id, song, singer, album, duration, url, picUrl, MusicSource.PLAYLIST.value)
        
        self._playindex = playindex
        self._playlist = list(map(format_playlist, res['songs']))
        # 保存文件到本地
        save_json(self.playlist_filepath, {
            'index': playindex,
            'list': json_list
        })

    # 获取当前播放音乐信息
    async def async_music_info(self):
        count = len(self.playlist)
        if count > 0:
           music_info = self.playlist[self._playindex]
           if music_info.source == MusicSource.PLAYLIST.value:
                # 获取播放链接
                res = await http_get(self.api_url + f'/song/url?id={music_info.id}', self.cookie)
                url = res['data'][0]['url']
                music_info._url = url
           return music_info

    # 下一曲
    def next(self):
        count = len(self.playlist)
        if count <= 1:
            return
        self._playindex = self._playindex + 1
        if self._playindex == count:
            self._playindex = 0

    # 上一曲
    def previous(self):
        count = len(self.playlist)
        if count <= 1:
            return
        self._playindex = self._playindex - 1
        if self._playindex < 0:
            self._playindex = count - 1