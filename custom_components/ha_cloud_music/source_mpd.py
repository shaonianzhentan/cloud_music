# MPD播放器
'''
python3 -m pip install python-mpd2
'''
import time, datetime
import threading

class MediaPlayerMPD():

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
        self._status = None        
        self._muted_volume = 0
        self._is_connected = False
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
            print((e))
            self.is_support = False

    def _connect(self):
        """Connect to MPD."""
        try:
            config = self.config
            # 连接MPD服务
            self._client.connect(config['mpd_host'], config.get('mpd_port', '6600'))
            if 'mpd_password' in config:
                self._client.password(config['mpd_password'])
            self.log('MPD服务连接成功')
        except Exception as ex:
            print((ex))
            return

        self._is_connected = True

    def _disconnect(self):
        """Disconnect from MPD."""
        self.log('MPD断开连接')
        try:
            self._client.disconnect()
        except Exception as ex:
            pass
        self._is_connected = False
        self._status = None

    @property
    def volume_level(self):
        # 获取音量
        if self._status is not None and "volume" in self._status:
            return int(self._status["volume"]) / 100
        return None

    def update(self):
        # 更新
        try:
            if not self._is_connected:
                self._connect()

            if self.is_tts == False:
                self._status = self._client.status()
                if self._status == None:
                    return None
                # currentsong = self._client.currentsong()
                # position = self._status.get("time")
                position = self._status.get("elapsed")
                # 读取音乐时长和进度
                media_position = 0
                #media_duration = 0
                if position is None:
                    position = self._status.get("time")
                    if isinstance(position, str) and ":" in position:
                        media_position = position.split(":")[0]
                        media_duration = position.split(":")[1]
                        if media_position is not None:
                            self.media_position = media_position
                        if media_duration is not None:
                            self.media_duration = media_duration
                        else:
                            self.media_duration = self._media._media_duration 
                            
                if position is not None :
                    media_position = int(float(position))
                    string_duration = self._status.get("duration")
                    if media_position is not None:
                        self.media_position = media_position
                    if string_duration is not None:
                        self.media_duration = int(float(string_duration))
                        #self._media._media_duration = self.media_duration
                    else:
                        self.media_duration = self._media._media_duration 
                        
                # 假如播放器的区间为0
                if self._media._media_duration == 0:
                    self._media._media_duration = self.media_duration
                if  media_position != 0:
                    self._media._media_position = media_position
                    self._media._media_position_updated_at = datetime.datetime.now()    
                # 判断是否下一曲
                self.log('当前进度：'+ str(media_position)  +'总时长:'+str(self.media_duration))
                if self.media_duration is not None and self.media_duration > 0:
                    # print("当前进度：%s，总时长：%s"%(media_position, media_duration))
                    if self.media_duration - media_position <= 3:
                        #self.log('剩余3s，下一曲方法')
                        if self._media is not None and self.state == 'playing' and self.is_on == True:
                            self.state = 'idle'
                            self.log('执行下一曲方法')
                            
                            self.media_duration = 0 
                            self.media_duration = 0
                            self._media._media_position = 0
                            self._media._media_duration = 0
                            self._media._media_position_updated_at = datetime.datetime.now()   
                            self._media.media_end_next()
                            
                #print("MPD当前进度：%s，总时长：%s"%(media_position, media_duration))
                
                self.media_position_updated_at = datetime.datetime.now()
        except Exception as e:
            self.log('出现异常:'+ str(e))
            #print('出现异常', e)
            self._disconnect()
        
        # 递归调用自己
        self.timer = threading.Timer(2, self.update)
        self.timer.start()  

    def reloadURL(self, url, position):
        # 重新加载URL
        self.load(url)
        time.sleep(1)
        # 先把声音设置为0，然后调整位置之后再还原
        self.set_volume_level(0)
        time.sleep(1)
        self.seek(position)
        time.sleep(1)
        self.set_volume_level(self._media.volume_level)

    def load(self, url):
        # 加载URL
        url = url.replace("https://", "http://")
        try:
            if self._status == None:
                return None
            self._client.clear()
            self._client.add(url)
            self._client.play()
        except Exception as ex:
            print('加载URL出现异常：', ex)
            self._connect()            
            self._client.clear()
            self._client.add(url)
            self._client.play()
        # 不是TTS时才设置状态
        if self.is_tts == False:
            self.state = 'playing'
        
    def play(self):
        if self._status == None:
            return None
        # 播放
        try:
            self.state = 'playing'
            self._client.pause(0)
        except Exception as e:
            self.log('出现异常1:'+ str(e))
    def pause(self):
        if self._status == None:
            return None
        # 暂停
        try:
            self.state = 'paused'
            self._client.pause(1)
        except Exception as e:
            self.log('出现异常2:'+ str(e))
    def seek(self, position):
        if self._status == None:
            return None
        # 设置进度
        try:
            self._client.seekcur(position)
        except Exception as e:
            self.log('出现异常3:'+ str(e))
    def mute_volume(self, mute):
        # 静音
        if self._status is not None and "volume" in self._status:
            if mute:
                self._muted_volume = self.volume_level
                self.set_volume_level(0)
            else:
                self.set_volume_level(self._muted_volume)
            self._muted = mute

    def set_volume_level(self, volume):
        # 设置音量
        if self._status is not None and "volume" in self._status:
            self._client.setvol(int(volume * 100))

    def volume_up(self):
        # 增加音量
        if self._status is not None and "volume" in self._status:
            current_volume = int(self._status["volume"])

            if current_volume <= 100:
                self._client.setvol(current_volume + 5)

    def volume_down(self):
        # 减少音量
        if self._status is not None and "volume" in self._status:
            current_volume = int(self._status["volume"])

            if current_volume >= 0:
                self._client.setvol(current_volume - 5)

    def stop(self):
        if self._status == None:
            return None
        # 停止
        try:
            self.timer.cancel()
            self._client.stop()
            self._client.disconnect()
        except Exception as e:
            self.log('出现异常4:'+ str(e))
    def set_rate(self, rate):
        # 设置播放速度
        return 1

    def log(self, msg):
        if self._media is not None:
            self._media.log(msg)
'''
mm = MediaPlayerMPD({'mpd_host': '192.168.1.113'})
if mm.is_support:
    mm.load('http://m10.music.126.net/20200726124850/bab67e3b8b368f2e029f8c918e20307f/ymusic/obj/w5zDlMODwrDDiGjCn8Ky/3253345932/a82c/c8f1/c240/74c34f5ed76bbb99c3022948717e56e4.mp3')
'''
