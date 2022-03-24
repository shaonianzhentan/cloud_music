import time, datetime
import threading

class MediaPlayerOther():

    # 初始化
    def __init__(self, entity_id, media=None):
        # 播放器相同字段
        self.entity_id = entity_id
        self._media = media
        self._muted = False
        self.rate = 1
        self.media_position = 0
        self.media_duration = 0
        self.media_position_updated_at = datetime.datetime.now()
        self.state = 'idle'
        self.is_tts = False
        self.is_on = True
        # 定时更新
        self.count = 0
        self.volume_level = 1
        self.timer = threading.Timer(1, self.update)
        self.timer.start()

    def update(self):
        # 更新
        try:
            hass = self._media._hass
            # 读取当前实体信息
            entity = hass.states.get(self.entity_id)
            attr = entity.attributes
            if 'media_position' in attr:
                media_position = attr['media_position']
                # 如果进度是字符串，并且包含冒号
                if isinstance(media_position, str) and ':' in media_position:
                    arr = media_position.split(':')
                    media_position = int(arr[0])
                    media_duration = int(arr[1])
                else:
                    media_duration = attr['media_duration']
                # print("当前进度：%s，总时长：%s"%(media_position, media_duration))
                # 判断是否下一曲
                if media_duration > 0:
                    if media_duration - media_position <= 5 or (media_position == 0 and entity.state == 'idle'):
                        print('执行下一曲方法')
                        if self._media is not None and self.state == 'playing' and self.is_tts == False and self.is_on == True and self.count > 0:
                            self.count = -5
                            self.state = 'idle'                            
                            self._media.media_end_next()
                    # 最后10秒时，实时更新
                    elif media_duration - media_position < 10:
                        print("当前进度：%s，总时长：%s"%(media_position, media_duration))
                        hass.async_create_task(hass.services.async_call('homeassistant', 'update_entity', {'entity_id': self.entity_id}))
                
                # 防止通信太慢，导致进度跟不上自动下下一曲
                self.count = self.count + 1
                if self.count > 100:
                    self.count = 0
                
                # 正常获取值
                self.media_position = media_position
                self.media_duration = media_duration
                self.volume_level = attr['volume_level']
                self.media_position_updated_at = datetime.datetime.now()
        except Exception as e:
            print('出现异常', e)
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
        self.call_service('play_media', {
            'media_content_id': url,
            'media_content_type': 'music'
        })
        # 不是TTS时才设置状态
        if self.is_tts == False:
            self.state = 'playing'

    def play(self):
        # 播放
        self.state = 'playing'
        self.call_service('media_play', {})
    
    def pause(self):
        # 暂停
        self.state = 'paused'
        self.call_service('media_pause', {})
    
    def seek(self, position):
        # 设置进度
        self.call_service('media_seek', {'seek_position': position})

    def mute_volume(self, mute):
        # 静音
        self.call_service('volume_mute', {'is_volume_muted': mute})

    def set_volume_level(self, volume):
        # 设置音量
        self.call_service('volume_set', {'volume_level': volume})

    def volume_up(self):
        # 增加音量
        self.call_service('volume_up', {})

    def volume_down(self):
        # 减少音量
        self.call_service('volume_down', {})

    def stop(self):
        # 停止
        self.pause()
        self.timer.cancel()

    def set_rate(self, rate):
        # 设置播放速度
        return 1

    def log(self, msg):
        if self._media is not None:
            self._media.log(msg, 'source_other')

    def call_service(self, service, data):
        hass = self._media._hass
        data.update({'entity_id': self.entity_id})
        hass.async_create_task(hass.services.async_call('media_player', service, data))