# Windows应用
import time, datetime
from homeassistant.components import websocket_api
import voluptuous as vol

WS_TYPE_MEDIA_PLAYER = "ha_windows_updated"
SCHEMA_WEBSOCKET = websocket_api.BASE_COMMAND_MESSAGE_SCHEMA.extend(
    {
        "type": WS_TYPE_MEDIA_PLAYER,
        vol.Optional("data"): dict,
    }
)

class MediaPlayerWindows():

    # 初始化
    def __init__(self, config, media=None):
        # 播放器相同字段
        self.config = config
        self._media = media
        self._muted = False
        self.rate = 1
        self.media_position = 0
        self.media_duration = 0
        self.media_position_updated_at = datetime.datetime.now()
        self.state = 'idle'
        self.is_tts = False
        self.is_on = True
        # 不同字段
        self.volume_level = 1
        self.is_support = True
        # 监听web播放器的更新
        if media is not None:
            self.hass = media._hass
            # 监听web播放器的更新
            print(WS_TYPE_MEDIA_PLAYER)
            self.hass.components.websocket_api.async_register_command(
                WS_TYPE_MEDIA_PLAYER,
                self.update,
                SCHEMA_WEBSOCKET
            )

    def update(self, hass, connection, msg):
        if self._media is not None:
            data = msg['data']
            # print(data)
            # 消息类型
            _type = data.get('type')
            if _type == 'music_info':
                self._muted = data.get('is_volume_muted', False)
                self._media._volume_level = data.get('volume_level', 1)
                self.media_position = data.get('media_position', 0)
                self.media_duration = data.get('media_duration', 0)
                self.media_position_updated_at = datetime.datetime.now()
            elif _type == 'music_end':
                self._media.media_end_next()
            elif _type == 'music_state':
                self.state = data.get('state')

    def reloadURL(self, url, position):
        # 重新加载URL
        self.load(url)
        # 先把声音设置为0，然后调整位置之后再还原
        volume_level = self._media.volume_level
        self.set_volume_level(0)
        # 局域网资源，则优化快进规则
        if self._media.base_url in url:
            time.sleep(0.1)
            self.seek(position)
        else:
            time.sleep(1)
            self.seek(position)
            time.sleep(1)
        # 如果重置是为0，则恢复正常
        if volume_level == 0:
            volume_level = 1
        self.set_volume_level(volume_level)

    def load(self, url):
        # 使用TTS服务
        if self.is_tts:
            self.fire_event({"type": "tts", "url": url})
        else:
            # 加载URL
            self.fire_event({"type": "load", "url": url})
            self.state = 'playing'

    def play(self):
        # 播放
        self.fire_event({"type": "play"})
        self.state = "playing"
    
    def pause(self):
        # 暂停
        self.fire_event({"type": "pause"})
        self.state = "paused"
    
    def seek(self, position):
        # 设置进度
        self.fire_event({"type": "media_position", "position": position})

    def mute_volume(self, mute):
        # 静音
        self.fire_event({"type": "is_volume_muted", "mute": mute})

    def set_volume_level(self, volume):
        # 设置音量
        self.fire_event({"type": "volume_set", "volume": volume})

    def volume_up(self):
        # 增加音量
        current_volume = self.volume_level
        if current_volume < 1:
            self.set_volume_level(current_volume + 0.1)

    def volume_down(self):
        # 减少音量
        current_volume = self.volume_level
        if current_volume > 0:
            self.set_volume_level(current_volume - 0.1)

    def stop(self):
        # 停止
        self.fire_event({"type": "pause"})

    def set_rate(self, rate):
        # 设置播放速度
        return 1

    def fire_event(self, data):
        self.hass.bus.fire("ha_windows", { 'type': 'music', 'music': data})