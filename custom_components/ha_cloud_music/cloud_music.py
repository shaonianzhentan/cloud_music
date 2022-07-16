import uuid, time, json, os, random
from .http_api import http_get
from .models.music_info import MusicInfo, MusicSource
from homeassistant.helpers.storage import STORAGE_DIR
from homeassistant.util.json import load_json, save_json

class CloudMusic():

    def __init__(self, url, uid) -> None:
        self.uid = uid
        self.api_url = url.strip('/')
        self.playlist_id = ''
        self.playindex = 0
        self._playlist = []
        self.cookie = {}
        # 读取本地存储文件
        self.playlist_filepath = self.get_storage_dir('cloud_music.playlist')
        if os.path.exists(self.playlist_filepath):
            res = load_json(self.playlist_filepath)
            self.playlist_id = res.get('id', '')
            self.playindex = res['index']
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
        # 读取cookie
        self.cookie_filepath = self.get_storage_dir('cloud_music.cookie')
        if os.path.exists(self.cookie_filepath):
            self.cookie = load_json(self.cookie_filepath)
    
    def get_storage_dir(self, file_name):
        return os.path.abspath(f'{STORAGE_DIR}/{file_name}')

    @property
    def playlist(self) -> list[MusicInfo]:
        return self._playlist

    # 网易云音乐接口
    async def netease_cloud_music(self, url):
        return await http_get(self.api_url + url, self.cookie)

    def save_file(self, name, data):
        filepath = self.get_storage_dir(f'cloud_music.{name}')
        save_json(filepath, data)
    
    def read_file(self, name):
        filepath = self.get_storage_dir(f'cloud_music.{name}')
        if os.path.exists(filepath):
            return load_json(filepath)

    def netease_image_url(self, url, size=200):
        return f'{url}?param={size}y{size}'

    # 加载播放列表
    async def async_load_playlist(self, playlist_id, playindex=0):
        playlist_id = str(playlist_id)
        # 如果相同歌单
        if self.playlist_id == playlist_id:
            self.playindex = playindex
            return
        # 获取歌单音乐
        self.playlist_id = playlist_id
        self.playindex = playindex
        self._playlist = await self.async_get_playlist(playlist_id)
        # 保存文件到本地
        self.save_playlist(playlist_id, MusicSource.PLAYLIST.value)

    async def async_load_djradio(self, playlist_id, playindex=0):
        playlist_id = str(playlist_id)
        # 如果相同歌单
        if self.playlist_id == playlist_id:
            self.playindex = playindex
            return
        # 获取歌单音乐
        self.playlist_id = playlist_id
        self.playindex = playindex
        self._playlist = await self.async_get_djradio(playlist_id)
        # 保存文件到本地
        self.save_playlist(playlist_id, MusicSource.DJRADIO.value)

    async def async_load_artists(self, playlist_id, playindex=0):
        playlist_id = str(playlist_id)
        # 如果相同歌单
        if self.playlist_id == playlist_id:
            self.playindex = playindex
            return
        # 获取歌单音乐
        self.playlist_id = playlist_id
        self.playindex = playindex
        self._playlist = await self.async_get_artists(playlist_id)
        # 保存文件到本地
        self.save_playlist(playlist_id, MusicSource.ARTISTS.value)

    async def async_load_cloud(self, playindex=0):
        playlist_id = 'cloud'
        # 如果相同歌单
        if self.playlist_id == playlist_id:
            self.playindex = playindex
            return
        # 获取歌单音乐
        self.playlist_id = playlist_id
        self.playindex = playindex
        self._playlist = await self.async_get_cloud()
        # 保存文件到本地
        self.save_playlist(playlist_id, MusicSource.CLOUD.value)

    # 保存播放记录
    def save_playlist(self, playlist_id, source):
        playlist = []
        for music_info in self.playlist:
            playlist.append(music_info.to_dict())
        # 保存文件到本地
        save_json(self.playlist_filepath, {
            'id': playlist_id,
            'source': source,
            'index': self.playindex,
            'list': playlist
        })

    # 获取当前播放音乐信息
    async def async_music_info(self):
        count = len(self.playlist)
        if count > 0:
           music_info = self.playlist[self.playindex]
           if music_info.source == MusicSource.PLAYLIST.value \
                or music_info.source == MusicSource.ARTISTS.value \
                or music_info.source == MusicSource.DJRADIO.value \
                or music_info.source == MusicSource.CLOUD.value:
                # 获取播放链接
                res = await self.netease_cloud_music(f'/song/url?id={music_info.id}')
                url = res['data'][0]['url']
                if url is not None:
                    music_info._url = url
                else:
                    # 从云盘里获取
                    res = await self.netease_cloud_music(f'/user/cloud')
                    filter_list = list(filter(lambda x:x['simpleSong']['id'] == music_info.id, res['data']))
                    if len(filter_list) > 0:
                        music_info.id = filter_list[0]['songId']
                        res = await self.netease_cloud_music(f'/song/url?id={music_info.id}')
                        music_info._url = res['data'][0]['url']
                    else:
                        # 全网音乐搜索
                        pass

           return music_info

    # 下一曲
    def next(self, shuffle=False):
        count = len(self.playlist)
        if shuffle:
            self.playindex = random.randint(0, count - 1)
            return
        if count <= 1:
            return
        self.playindex = self.playindex + 1
        if self.playindex == count:
            self.playindex = 0

    # 上一曲
    def previous(self):
        count = len(self.playlist)
        if count <= 1:
            return
        self.playindex = self.playindex - 1
        if self.playindex < 0:
            self.playindex = count - 1

    # 获取歌单列表
    async def async_get_playlist(self, playlist_id):
        res = await self.netease_cloud_music(f'/playlist/track/all?id={playlist_id}')

        def format_playlist(item):
            id = item['id']
            song = item['name']
            singer = item['ar'][0]['name']
            album = item['al']['name'] 
            duration = item['dt']
            url = ''
            picUrl = item['al'].get('picUrl', 'https://p2.music.126.net/fL9ORyu0e777lppGU3D89A==/109951167206009876.jpg')
            music_info = MusicInfo(id, song, singer, album, duration, url, picUrl, MusicSource.PLAYLIST.value)
            return music_info
        
        return list(map(format_playlist, res['songs']))

    # 获取电台列表
    async def async_get_djradio(self, rid):
        res = await self.netease_cloud_music(f'/dj/program?rid={rid}&limit=200')

        def format_playlist(item):
            mainSong = item['mainSong']
            id = mainSong['id']
            song = mainSong['name']
            singer = mainSong['artists'][0]['name']
            album = item['dj']['brand']
            duration = mainSong['duration']
            url = ''
            picUrl = item['coverUrl']
            music_info = MusicInfo(id, song, singer, album, duration, url, picUrl, MusicSource.DJRADIO.value)
            return music_info
        
        return list(map(format_playlist, res['programs']))

    # 获取歌手列表
    async def async_get_artists(self, aid):
        res = await self.netease_cloud_music(f'/artists?id={aid}')

        def format_playlist(item):
            id = item['id']
            song = item['name']
            singer = item['ar'][0]['name']
            album = item['al']['name']
            duration = item['dt']
            url = ''
            picUrl = res['artist']['picUrl']
            music_info = MusicInfo(id, song, singer, album, duration, url, picUrl, MusicSource.ARTISTS.value)
            return music_info
        
        return list(map(format_playlist, res['hotSongs']))

    # 获取云盘音乐
    async def async_get_cloud(self):
        res = await self.netease_cloud_music('/user/cloud')
        def format_playlist(item):
            id = item['songId']
            singer = ''
            duration = ''
            url = ''
            album = ''
            picUrl = 'http://p3.music.126.net/ik8RFcDiRNSV2wvmTnrcbA==/3435973851857038.jpg'

            simpleSong = item.get('simpleSong')
            if simpleSong is not None:
                song = simpleSong.get("name")
                duration = simpleSong.get("dt")
                al = simpleSong.get('al')
                if al is not None:
                    picUrl = al.get('picUrl')
                    album = al.get('name')
                ar = simpleSong.get('ar')
                if ar is not None and len(ar) > 0:
                    singer = ar[0].get('name', '')

            music_info = MusicInfo(id, song, singer, album, duration, url, picUrl, MusicSource.CLOUD.value)
            return music_info
        
        return list(map(format_playlist, res['data']))