import threading, datetime

class MediaPlayerMPD():

    # 初始化
    def __init__(self, media_player):
        self.media_player = media_player
        self.hass = media_player.hass
        try:
            import mpd
            self._client = mpd.MPDClient()
            self._client.timeout = 30
            self._client.idletimeout = None
            self._connect()
            self.is_support = True
            # 定时更新
            self.timer = threading.Timer(1, self.update)
            self.timer.start()
        except Exception as e:
            print(e)
            self.is_support = False

    def update(self):
        if not self._is_connected:
            self._connect()
            status = self._client.status()
            # 音量
            volume_level = int(status.get("volume")) / 100
            self.media_player._attr_volume_level = volume_level
            self.media_player._attr_is_volume_muted = volume_level == 0
            # 读取音乐时长和进度
            position = status.get("time")
            media_position = 0
            media_duration = 0
            if isinstance(position, str) and ':' in position:
                arr = position.split(':')
                media_position = int(arr[0])
                media_duration = int(arr[1])
            # 进度
            self.media_player._attr_media_position = media_position
            self.media_player._attr_media_position_updated_at = datetime.datetime.now()
            # 总时长
            self.media_player._attr_media_duration = media_duration

        # 递归调用自己
        self.timer = threading.Timer(2, self.update)
        self.timer.start()
 
    async def async_media_play(self):
        # 播放
        self._client.pause(0)
    
    async def async_media_pause(self):
        # 暂停
        self._client.pause(1)
    
    async def async_media_seek(self, position):
        # 设置进度
        self._client.seekcur(position)

    async def async_mute_volume(self, mute):
        # 静音
        if mute:
            await self.async_set_volume_level(1)
        else:
            await self.async_set_volume_level(0.5)

    async def async_set_volume_level(self, volume):
        # 设置音量
        self._client.setvol(int(volume * 100))

    async def async_volume_up(self):
        # 增加音量
        current_volume = self.media_player._attr_volume_level
        if current_volume < 1:
            self.set_volume_level(current_volume + 0.1)

    async def async_volume_down(self):
        # 减少音量
        current_volume = self.media_player._attr_volume_level
        if current_volume > 0:
            self.set_volume_level(current_volume - 0.1)

    async def async_play_media(self, media_type, media_id):
        print(media_type, media_id)
        #self._client.clear()
        #self._client.add(media_id)
        #self._client.play()

    async def async_media_stop(self):
        self.timer.cancel()
        self._client.stop()
        self._client.disconnect()

    def _connect(self):
        try:
            config = self.media_player.config
            mpd_host = config.get('mpd_host')
            mpd_port = config.get('mpd_port', 6600)
            mpd_password = config.get('mpd_password', '')
            # 连接MPD服务
            self._client.connect(mpd_host, mpd_port)
            if mpd_password != '':
                self._client.password(mpd_password)
            print('MPD服务连接成功')
            self._is_connected = True
        except Exception as ex:
            self._is_connected = False
            print(ex)

    def _disconnect(self):
        print('MPD断开连接')
        try:
            self._client.disconnect()
        except Exception as ex:
            pass
        self._is_connected = False