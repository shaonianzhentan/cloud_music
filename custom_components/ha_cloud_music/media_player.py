import json, os, logging, time, datetime, random, re, uuid, math, base64, asyncio, aiohttp
from homeassistant.components.media_player import MediaPlayerEntity
from homeassistant.helpers.network import get_url
from homeassistant.components.media_player.const import (
    MEDIA_TYPE_MUSIC,MEDIA_TYPE_URL, SUPPORT_PAUSE, SUPPORT_PLAY, SUPPORT_BROWSE_MEDIA, 
    SUPPORT_NEXT_TRACK, SUPPORT_PREVIOUS_TRACK, SUPPORT_TURN_ON, SUPPORT_TURN_OFF, SUPPORT_STOP,
    SUPPORT_PLAY_MEDIA, SUPPORT_VOLUME_MUTE, SUPPORT_VOLUME_SET, SUPPORT_SELECT_SOURCE, SUPPORT_CLEAR_PLAYLIST, 
    SUPPORT_SELECT_SOUND_MODE, SUPPORT_SEEK, SUPPORT_VOLUME_STEP)
from homeassistant.const import (STATE_IDLE, STATE_PAUSED, STATE_PLAYING, STATE_OFF, STATE_UNAVAILABLE)
from homeassistant.components.media_player.errors import BrowseError
from .browse_media import build_item_response, library_payload

from .api_kuwo import check_163_song_url, search_kuwo_music_by_keyword

# SUPPORT_TURN_ON | SUPPORT_TURN_OFF | 
SUPPORT_FEATURES = SUPPORT_PAUSE | SUPPORT_VOLUME_SET | SUPPORT_VOLUME_MUTE | SUPPORT_SELECT_SOUND_MODE | \
    SUPPORT_PLAY_MEDIA | SUPPORT_PLAY | SUPPORT_NEXT_TRACK | \
    SUPPORT_PREVIOUS_TRACK | SUPPORT_SELECT_SOURCE | SUPPORT_CLEAR_PLAYLIST | SUPPORT_SEEK | SUPPORT_VOLUME_STEP | \
    SUPPORT_BROWSE_MEDIA

_LOGGER = logging.getLogger(__name__)
################### 接口定义 ###################
# 常量
from .const import DOMAIN, VERSION, ROOT_PATH, WEB_PATH, NAME, ICON
from .api_config import ApiConfig
# 网易云接口
from .api_music import ApiMusic
# 网关视图
from .api_view import ApiView
# 语音接口
from .api_voice import ApiVoice
# TTS接口
from .api_tts import ApiTTS
# 播放器
from .source_web import MediaPlayerWEB
from .source_vlc import MediaPlayerVLC
from .source_mpd import MediaPlayerMPD
from .source_other import MediaPlayerOther

def setup_platform(hass, config, add_entities, discovery_info=None):
    # 显示模式 全屏：fullscreen
    show_mode = config.get("show_mode", "default")
    
    # TTS相关配置
    tts_before_message = config.get("tts_before_message", '')
    tts_after_message = config.get("tts_after_message", '')
    tts_mode = config.get("tts_mode", 4)

    #### （启用/禁用）配置 #### 

    # 是否开启语音文字处理程序（默认启用）
    is_voice = config.get('is_voice', True)

    ################### 系统配置 ###################

    ################### 定义实体类 ###################    
    # 播放器实例
    api_config = ApiConfig(hass.config.path(".shaonianzhentan/ha_cloud_music"))
    # 创建媒体文件夹
    api_config.mkdir(hass.config.path("media/ha_cloud_music"))
    mp = MediaPlayer(hass, config, api_config)
    # 是否启用通知（默认启用）
    mp.is_notify = config.get('is_notify', True)
    
    mp.api_tts = ApiTTS(mp,{
        'tts_before_message': tts_before_message,
        'tts_after_message': tts_after_message,
        'tts_mode': tts_mode
    })    
    mp.api_music = ApiMusic(mp, config)    
    # 检测配置
    if mp.api_music.api_url == '':
        mp.notify("检测到未配置api_url参数！", "error")
        return
    # 开始登录    
    hass.async_create_task(mp.api_music.login())
    
    hass.data[DOMAIN] = mp
    # 添加实体
    add_entities([mp])

    ################### 定义实体类 ###################

    ################### 注册服务 ################### 
    # 注册服务【加载歌单】
    hass.services.async_register(DOMAIN, 'load', mp.load_songlist)

    # 注册服务【点歌】
    hass.services.async_register(DOMAIN, 'pick', mp.pick_song)

    # 注册服务【配置】
    hass.services.async_register(DOMAIN, 'config', mp.config)

    # 注册服务【tts】
    hass.services.async_register(DOMAIN, 'tts', mp.api_tts.speak)

    # 注册服务【缓存文件】
    hass.services.async_register(DOMAIN, 'cache', mp.cache)

    # 监听语音小助手的文本
    if is_voice == True:
        _ApiVoice = ApiVoice(hass, mp.api_music)
        hass.bus.async_listen('ha_voice_text_event', _ApiVoice.text_event)

    ################### 注册服务 ################### 

    # 显示插件信息
    _LOGGER.info('''
-------------------------------------------------------------------
    ha_cloud_music云音乐插件【作者QQ：635147515】
    
    版本：''' + VERSION + '''    
    
    介绍：这是一个网易云音乐的HomeAssistant播放器插件
    
    项目地址：https://github.com/shaonianzhentan/ha_cloud_music
    
    配置信息：
    
        API_URL：''' +  mp.api_music.api_url + '''
        
        显示模式：''' + (show_mode == 'fullscreen' and '全局模式' or '默认模式') + '''
        
        用户ID：''' + mp.api_music.uid + '''

-------------------------------------------------------------------''')
################### 注册静态目录与接口网关 ###################
    # 注册静态目录
    hass.http.register_static_path(ROOT_PATH, hass.config.path("custom_components/ha_cloud_music/dist"), False)
    hass.http.register_static_path('/tts-local', hass.config.path("tts"), False)
    hass.http.register_static_path('/media-local', hass.config.path("media/ha_cloud_music"), False)
    hass.http.register_static_path(WEB_PATH, hass.config.path("custom_components/ha_cloud_music/local"), False)
    # 注册网关接口
    hass.http.register_view(ApiView)
    # 注册菜单栏
    hass.components.frontend.async_register_built_in_panel(
        "iframe", NAME, ICON, DOMAIN,
        { "url": ROOT_PATH + "/index.html?ver=" + VERSION
        + "&show_mode=" + show_mode
        + "&uid=" + mp.api_music.uid },
        require_admin=False
    )
    # 添加状态卡片
    hass.components.frontend.add_extra_js_url(hass, WEB_PATH + '/card/ha_cloud_music.js?v=' + VERSION)
    ################### 注册静态目录与接口网关 ###################
    return True   

# 集成安装
async def async_setup_entry(hass, config_entry, async_add_entities):
    setup_platform(hass, config_entry.data, async_add_entities)
    return True

###################媒体播放器##########################
class MediaPlayer(MediaPlayerEntity):

    def __init__(self, hass, config, api_config):
        self._config = config
        self.api_config = api_config

        self._hass = hass
        self.music_playlist = None
        self.music_index = 0
        self.media_url = None
        self._media_image_url = None
        self._media_title = None
        self._media_name = ''
        self._media_artist = None
        self._media_album_name = None
        # 媒体播放器
        self._media_player = None
        # 音量
        self._volume_level = 1
        # 喜欢
        self.favourite = False

        self._source_list = None
        self._source = None
        # 播放模式（0：列表循环，1：顺序播放，2：随机播放，3：单曲循环）
        self._play_mode = 0
        self._media_position_updated_at = None
        self._media_position = 0
        self._media_duration = None
        
        # 错误计数
        self.error_count = 0
        self.loading = False
        # 是否启用定时器
        self._timer_enable = True
        self.is_notify = True

        _sound_mode_list = ['网页播放器']
            
        mpd_host = config.get('mpd_host', '')
        # 如果是Docker环境，则不显示VLC播放器
        if os.path.isfile("/.dockerenv") == True and mpd_host != '':
            _sound_mode_list.append('MPD播放器')
        else:
            _sound_mode_list.append('VLC播放器')
            # 如果有配置mpd，则显示MPD播放器
            if mpd_host != '':
                _sound_mode_list.append('MPD播放器')

        self._sound_mode_list = _sound_mode_list
        self._sound_mode = None
        # 读取播放器配置
        res = self.api_config.get_sound_mode()
        if res is not None:
            self.select_sound_mode(res['state'])

        # 读取音乐列表
        try:
            res = self.api_config.get_playlist()
            if res is not None:
                self.music_playlist = res['playlist']
                self.music_index = int(res['index'])
                self._volume_level = float(res.get('volume_level', 1))
                source_list = []
                for index in range(len(self.music_playlist)):
                    music_info = self.music_playlist[index]
                    _source = str(index + 1) + '.' + music_info['song'] + ' - ' + music_info['singer']
                    if self.music_index == index:
                        self._source = _source
                    source_list.append(_source)
                self._source_list = source_list
        except Exception as ex:
            pass

    def update(self):
        # 数据更新
        return True

    @property
    def name(self):
        # 设备的名称
        return "云音乐"

    @property
    def supported_features(self):
        return SUPPORT_FEATURES

    @property
    def media_content_type(self):
        return MEDIA_TYPE_MUSIC

    @property
    def state_attributes(self):
        # 当前媒体状态属性
        attr = super().state_attributes
        play_mode_list = ['列表循环','顺序播放','随机播放','单曲循环']
        attr.update({'custom_ui_more_info': 'ha_cloud_music-panel',
            'custom_ui_state_card': 'ha_cloud_music-player',
            'tts_volume': self.api_tts.tts_volume,
            'tts_mode': self.api_tts.tts_mode,
            'media_url': self.media_url,
            'media_rate': self.media_rate,
            'favourite': self.favourite,
            'version': VERSION,
            'play_mode': play_mode_list[self._play_mode]})
        return attr

    @property
    def device_class(self):
        return 'tv'

    @property
    def media_image_url(self):
        # 当前播放的音乐封面地址.
        if self._media_image_url != None:            
            return self._media_image_url + "?param=500y500"
        return self._media_image_url
        
    @property
    def media_image_remotely_accessible(self) -> bool:
        # 图片远程访问
        return True
    
    @property
    def source_list(self):
        # 音乐列表 
        return self._source_list   

    @property
    def source(self):
        # 当前播放音乐
        return self._source       
        
    @property
    def sound_mode_list(self):
        # 播放器列表
        return self._sound_mode_list

    @property
    def sound_mode(self):
        # 当前播放器
        return self._sound_mode
    
    @property
    def media_album_name(self):
        """专辑名称."""
        return self._media_album_name
    
    @property
    def media_playlist(self):
        """当前播放列表"""
        return self.music_playlist
    
    @property
    def media_title(self):
        """歌曲名称."""
        return self._media_title
        
    @property
    def media_artist(self):
        """歌手"""
        return self._media_artist
        
    @property
    def state(self):
        # 返回当前播放器状态
        if self._media_player == None:
            return STATE_IDLE
        if self._media_player.state == 'playing':
            return STATE_PLAYING
        elif self._media_player.state == 'paused':
            return STATE_PAUSED
        return STATE_IDLE

    @property
    def volume_level(self):
        return self._volume_level

    @property
    def is_volume_muted(self):
        if self._media_player == None:
            return None
        return self._media_player._muted

    @property
    def media_rate(self):
        if self._media_player == None:
            return 1
        return self._media_player.rate

    @property
    def media_duration(self):
        if self._media_player == None:
            return None
        return self._media_player.media_duration

    @property
    def media_position(self):
        if self._media_player == None:
            return None
        return self._media_player.media_position
		
    @property
    def media_position_updated_at(self):
        if self._media_player == None:
            return None
        return self._media_player.media_position_updated_at

    @property
    def base_url(self):
        return get_url(self._hass)

    def turn_off(self):
        print("关闭设备")
        if self._media_player == None:
            return None
        self._media_player.is_on = False

    def turn_on(self):
        print("打开设备")
        if self._media_player == None:
            return None
        self._media_player.is_on = True

    def media_seek(self, position):
        """将媒体设置到特定位置."""
        if self._media_player == None:
            return None
        self.log('【设置播放位置】：%s', position)
        self._media_player.seek(position)
        self.update_entity()

    def mute_volume(self, mute):
        """静音."""
        if self._media_player == None:
            return None
        self._media_player.mute_volume(mute)
        self.update_entity()

    def set_volume_level(self, volume):
        """Set volume level, range 0..1."""
        if self._media_player == None:
            return None
        self.log('【设置音量】：%s', volume)
        self._volume_level = volume
        self._media_player.set_volume_level(volume)
        self.update_entity()

    def media_play(self):
        """Send play command."""
        if self._media_player == None:
            return None
        self._media_player.play()
        self.update_entity()

    def media_pause(self):
        """Send pause command."""
        if self._media_player == None:
            return None
        self._media_player.pause()
        self.update_entity()

    def media_stop(self):
        """Send stop command."""
        if self._media_player == None:
            return None
        self._media_player.pause()
		
    async def async_play_media(self, media_type, media_id, **kwargs):
        ''' 异步方法 '''
        await self.play_media(media_type, media_id)

    async def play_media(self, media_type, media_id, **kwargs):
        is_bind_source_list = False
        # 播放媒体URL文件
        self.log('【播放列表类型】：%s', media_type)
        if media_type == MEDIA_TYPE_MUSIC:
            url = media_id
        elif media_type == 'music_load':                    
            self.music_index = int(media_id)
            music_info = self.music_playlist[self.music_index]            
            url = await self.get_url(music_info)
            # 保存音乐播放列表到本地
            self.api_config.set_playlist(self)
        elif media_type == MEDIA_TYPE_URL:
            self.log('加载播放列表链接：%s', media_id)
            play_list = await self.api_music.proxy_get(media_id)
            self.music_playlist = play_list
            music_info = self.music_playlist[0]
            url = await self.get_url(music_info)
            #数据源
            is_bind_source_list = True
        elif media_type == 'music_playlist':
            self.log('初始化播放列表')
            # 如果是list类型，则进行操作
            if isinstance(media_id, list):
                self.music_playlist = media_id
                self.music_index = 0
            elif isinstance(media_id, dict):
                _dict = media_id
                self.music_playlist = _dict['list']
                self.music_index = _dict['index']
            else:
                self.notify("播放数据错误", "error")
                return

            # 保存音乐播放列表到本地
            self.api_config.set_playlist(self)
                        
            music_info = self.music_playlist[self.music_index]
            url = await self.get_url(music_info)
            #数据源
            is_bind_source_list = True
        elif 'library_' in media_type:
            # 本地音乐库
            music_playlist = self.api_music.get_local_media_list(media_type)
            if len(music_playlist) == 0:
                return None
            self.music_playlist = music_playlist
            self.music_index = 0
            url = self.music_playlist[self.music_index]['url']
            #数据源
            is_bind_source_list = True
        else:
            _LOGGER.error(
                "不受支持的媒体类型 %s",media_type)
            return
        self.log('【当前播放音乐】【%s】:【%s】'%(self._media_name, url))

        # 绑定数据源
        if is_bind_source_list:
            source_list = []
            for index in range(len(self.music_playlist)):
                music_info = self.music_playlist[index]
                source_list.append(str(index + 1) + '.' + music_info['song'] + ' - ' + music_info['singer'])
            self._source_list = source_list
        try:
            # 如果没有url则下一曲（如果超过3个错误，则停止）
            # 如果是云音乐播放列表 并且格式不是mp3不是m4a，则下一曲
            if url is None or (media_type == 'music_load' and url.find(".mp3") < 0 and url.find(".flac") < 0  and url.find('.m4a') < 0):
               self.notify("没有找到【" + self._media_name + "】的播放链接，自动为您跳到下一首", "error")
               self.error_count = self.error_count + 1
               if self.error_count < 3:
                 self.media_next_track()
               return
            else:
                self.notify("正在播放【" + self._media_name + "】", "load_song_url")
        except Exception as e:
            print('这是一个正常的错误：', e)

        # 加载音乐
        if self._media_player is None:
            self.notify("请重新选择源播放器", "error")
        else:
            self.media_url = url
            self._media_player.load(url)

    # 音乐结束自动下一曲
    def media_end_next(self):        
        playlist_count = len(self.music_playlist) - 1
        # 如果是顺序播放，最后一曲，则暂停
        if self._play_mode == 1 and self.music_index >= playlist_count:
            return
        # 如果是单曲循环，则索引往前移一位
        if self._play_mode == 3:
            self.music_index = self.music_index - 1
        # 如果启用了随机模式，则每次都生成随机值
        elif self._play_mode == 2:
           # 这里的索引会在下一曲后加一
           self.music_index = random.randint(0, playlist_count)           

        self.media_next_track()

    def media_next_track(self):
        # 下一曲
        self.music_index = self.music_index + 1
        self.log('【下一曲】：%s', self.music_index)
        self.music_load()

    def media_previous_track(self):
        # 上一曲
        self.music_index = self.music_index - 1
        self.log('【上一曲】：%s', self.music_index)
        self.music_load()
    
    def select_source(self, source):
        # 选择音乐
        self.log('【选择音乐】：%s', source)
        self.music_index = self._source_list.index(source)
        self.music_load()
        self.update_entity()
        
    def select_sound_mode(self, sound_mode):
        print(sound_mode)
        # 相同不做处理
        if self._sound_mode == sound_mode:
            return None
        
        # 如果当前正在播放，则保存相关信息
        is_playing = self.state == STATE_PLAYING
        media_url = self.media_url
        media_position = self.media_position
        
        # 选择播放器
        if self._media_player is not None:
            try:
                self._media_player.stop()
                time.sleep(1)
            except Exception as ex:
                print(ex)
                self._media_player = None
                self.notify(self._sound_mode + "连接异常", "error")

        if sound_mode == '网页播放器':
            self._media_player = MediaPlayerWEB(self._config, self)
        elif sound_mode == 'MPD播放器':
            # 判断是否配置mpd_host
            if 'mpd_host' not in self._config:
                self.notify("MPD播放器需要配置mpd_host", "error")
                self._media_player = None
            self._media_player = MediaPlayerMPD(self._config, self)
            if self._media_player.is_support == False:
                self.notify("不支持MPD播放器，请确定是否正确配置", "error")
                self._media_player = None
        elif sound_mode == 'VLC播放器':
            self._media_player = MediaPlayerVLC(self._config, self)
            if self._media_player.is_support == False:
                self.notify("当前系统不支持VLC播放器", "error")
                self._media_player = None
        else:
            self._media_player = MediaPlayerOther(sound_mode, self)

        if self._media_player is not None:
            self._sound_mode = sound_mode
            self.api_config.set_sound_mode(sound_mode)
            self.log('【选择源播放器】：%s', sound_mode)
            # 恢复播放
            if is_playing == True:
                self._media_player.reloadURL(media_url, media_position)

    async def async_browse_media(self, media_content_type=None, media_content_id=None):
        """Implement the websocket media browsing helper."""
        if media_content_type in [None, "library"]:
            return await self._hass.async_add_executor_job(library_payload, self)

        payload = {
            "search_type": media_content_type,
            "search_id": media_content_id,
        }
        response = await build_item_response(self, payload)
        if response is None:
            raise BrowseError(
                f"Media not found: {media_content_type} / {media_content_id}"
            )
        return response

    ###################  自定义方法  ##########################

    async def get_url(self, music_info):
        # 当前资源类型
        _id = music_info.get('id', -1)
        _type =  music_info.get('type', '')
        self._media_name = music_info['song'] + ' - ' + music_info['singer']
        self._source = str(self.music_index + 1) + '.' + self._media_name
        # 歌名
        self._media_title = music_info['song']
        # 歌手
        self._media_artist = music_info['singer']
        # 设置图片
        if 'image' in music_info:
            self._media_image_url = music_info['image']
        # 设置专辑名称
        if 'album' in music_info:
            self._media_album_name = music_info['album']
        # 查看是否加入喜欢
        self.favourite = self.api_config.is_love_playlist(_id, _type)
        if 'duration' in music_info and music_info['duration'] != 0 :
            self._media_duration = music_info['duration']
        if _type == 'url':
            # 如果传入的是能直接播放的音频
            return music_info['url']
        elif _type == 'djradio' or _type == 'cloud':
            # 如果传入的是网易电台
            url = await self.api_music.get_song_url(_id)
            return url
        elif _type == 'qq':                
            # 如果传入的是QQ音乐
            url = await self.api_music.get_qq_song_url(music_info['mid'])
            return url
        elif _type == 'xmly':
            # 喜马拉雅资源
            _url = music_info.get('url', '')
            if _url != '':
                # 判断当前资源是否可用
                http_code = await self.api_music.get_http_code(_url)
                if http_code == 200:
                    return _url
            print('当前音频只有尊贵的喜马拉雅VIP会员才能收听。。。尝试解析中。。。')
            url = await self.api_music.get_ximalaya_vip_audio_url(_id)
            if url is None:
                self.notify("该音频只有尊贵的喜马拉雅VIP会员才能收听😂", "error")
            return url

        url = await self.api_music.get_redirect_url(music_info['url'])
                
        # 如果传入的是能直接播放的音频
        #if music_info['url'].startswith('https://music.163.com/song/media/outer/url'):
            #url = await check_163_song_url(_id, music_info['song'], music_info['singer'], music_info['url'])
            #self.log("【替换前url为：】:%s", url)
            #music_info['url'] = url
            # 如果没有url，则去kuwo搜索
        if url == None:
            url = await search_kuwo_music_by_keyword(_id,music_info['song'], music_info['singer'])
            music_info['url'] = url
        else:
            music_info['url'] = url
        self.log("【替换后url为：】:%s", url)
        # 如果没有url，则去咪咕搜索
        if url == None:
            url = await self.api_music.migu_search(music_info['song'], music_info['singer'])
        return url
                            
    def music_load(self):
        if self.music_playlist == None:
           self.log('【结束播放，没有播放列表】')
           return
        playlist_count = len(self.music_playlist)
        if self.music_index >= playlist_count:
           self.music_index = 0
        elif self.music_index < 0:
           self.music_index = playlist_count - 1
        self._hass.async_create_task(self.play_media('music_load', self.music_index))

    # 设置播放模式
    def set_play_mode(self, _mode):
        mode_names = ['列表循环', '顺序播放', '随机播放', '单曲循环']
        mode_list = [0, 1, 2, 3]
        if mode_list.count(_mode) == 0:
            _mode = 0
        self._play_mode = _mode
        self.log('【设置播放模式】：%s', mode_names[_mode])

    ######### 服务 ##############
    def config(self, call):
        _obj = call.data
        self.log('【调用内置服务】 %s', _obj)
        # 设置播放模式
        if 'play_mode' in _obj:
            self.set_play_mode(_obj['play_mode'])
        # 设置播放速度
        if 'media_rate' in _obj:
            media_rate = float(_obj['media_rate'])
            if self._media_player is not None and media_rate > 0 and media_rate < 3:
                self._media_player.set_rate(media_rate)
        # 设置TTS声音模式
        if 'tts_mode' in _obj:
            mode_list = [1, 2, 3, 4]
            _mode = _obj['tts_mode']
            if mode_list.count(_mode) == 0:
                _mode = 4
            self.api_tts.tts_mode = _mode
            self.notify('设置TTS声音模式：' + str(_mode), 'config')
            # 保存TTS配置
            self.api_config.set_tts(self.api_tts.tts_mode, self.api_tts.tts_volume)
        # 设置TTS音量
        if 'tts_volume' in _obj:
            tts_volume = int(_obj['tts_volume'])
            if 1 <= tts_volume <= 100:
                self.api_tts.tts_volume = tts_volume
                self.notify('设置TTS音量到' + str(tts_volume), 'config')
                # 保存TTS配置
                self.api_config.set_tts(self.api_tts.tts_mode, self.api_tts.tts_volume)
        # （禁用/启用）通知
        if 'is_notify' in _obj:
            is_notify = bool(_obj['is_notify'])
            _str = is_notify and '启用通知' or '禁用通知'
            # 如果没有启用通知，则现在启用
            if self.is_notify == False:
                self.is_notify = True
            self.notify(_str, 'config')
            self.is_notify = is_notify
        
        self.update_entity()

    # 缓存文件
    async def cache(self, call):
        data = call.data
        url = data['url']
        name = data['name']
        await self.api_music.cache_file(url, name)

    # 加载播放列表
    async def load_songlist(self, call): 
        list_index = 0
        # 如果传入了id和type，则按最新的服务逻辑来操作
        if 'id' in call.data and 'type' in call.data:
            _id = call.data['id']
            if call.data['type'] == 'playlist':
                _type = "playlist"
            elif call.data['type'] == 'djradio':
                _type = "djradio"
            elif call.data['type'] == 'ximalaya':
                _type = "ximalaya"
            else:
                self.notify("加载播放列表：type参数错误", "error")
                return "type参数错误"
        elif 'id' in call.data:
            _id = call.data['id']
            _type = "playlist"
        elif 'rid' in call.data:
            _id = call.data['rid']
            _type = "djradio"
        
        # 新的参数
        if 'index' in call.data:
            list_index = int(call.data['index']) - 1
        if self.loading == True:
            self.notify("正在加载歌单，请勿重复调用服务", "load_songlist")
            return
        self.loading = True

        try:
            if _type == "playlist":
                self.log("【加载歌单列表】，ID：%s", _id)
                # 获取播放列表
                obj = await self.api_music.music_playlist(_id)      
                if obj != None and len(obj['list']) > 0:
                    _newlist = obj['list']
                    if list_index < 0 or list_index >= len(_newlist):
                        list_index = 0
                    self.music_index = list_index
                    await self.play_media('music_playlist', _newlist)
                    self.notify("正在播放歌单【"+obj['name']+"】", "load_songlist")
                else:
                    # 这里弹出提示
                    self.notify("没有找到id为【"+_id+"】的歌单信息", "load_songlist")
            elif _type == "djradio":
                self.log("【加载电台列表】，ID：%s", _id)
                # 获取播放列表
                offset = 0
                if list_index >= 50:
                   offset = math.floor((list_index + 1) / 50)
                # 取余
                list_index = list_index % 50
                _list = await self.api_music.djradio_playlist(_id, offset, 50)
                if len(_list) > 0:
                    self.music_index = list_index
                    await self.play_media('music_playlist', _list)
                    self.notify("正在播放专辑【" + _list[0]['album'] + "】", "load_songlist")
                else:
                    self.notify("没有找到id为【"+_id+"】的电台信息", "error")
            elif _type == 'ximalaya':
                self.log("【加载喜马拉雅专辑列表】，ID：%s", _id)
                # 播放第几条音乐
                music_index = list_index % 50
                # 获取第几页
                list_index =  math.floor(list_index / 50) + 1
                _list = await self.api_music.ximalaya_playlist(_id, list_index, 50)
                if len(_list) > 0:
                    self.music_index = music_index
                    await self.play_media('music_playlist', _list)
                    self.notify("正在播放专辑【" + _list[0]['album'] + "】", "load_songlist")
                else:
                    self.notify("没有找到id为【"+_id+"】的专辑信息", "error")
                    
        except Exception as e:
            self.log(e)
            self.notify("加载歌单的时候出现了异常", "error")
        finally:
            # 这里重置    
            self.loading = False
        # 更新实体
        self.update_entity()

    # 单曲点歌
    async def pick_song(self, call): 
        if 'name' in call.data:
            _name = call.data['name']
            self.log("【单曲点歌】，歌名：%s", _name)
            await self.api_music.play_song(_name)

    ###################  系统服务  ##########################
    # 调用服务
    def call_service(self, domain, service, data):
        self._hass.async_create_task(self._hass.services.async_call(domain, service, data))

    # 日志
    def log(self, *args):
        _LOGGER.info(*args)
    
    # 更新实体
    def update_entity(self):
        time.sleep(1)
        self.call_service('homeassistant', 'update_entity', {'entity_id': 'media_player.yun_yin_le'})

    # 通知
    def notify(self, message, type):
        # 开启通过，或者错误提示，则显示通知
        if self.is_notify or type == "error":
            self.call_service('persistent_notification', 'create', {"message": message, "title": "云音乐", "notification_id": "ha-cloud-music-" + type})