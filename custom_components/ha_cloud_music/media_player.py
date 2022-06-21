import logging, time, datetime

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.storage import STORAGE_DIR
from homeassistant.components.media_player import MediaPlayerEntity, MediaPlayerDeviceClass
from homeassistant.components.media_player.const import (
    SUPPORT_BROWSE_MEDIA,
    SUPPORT_TURN_OFF,
    SUPPORT_TURN_ON,
    SUPPORT_VOLUME_STEP,
    SUPPORT_VOLUME_SET,
    SUPPORT_VOLUME_MUTE,
    SUPPORT_SELECT_SOURCE,
    SUPPORT_SELECT_SOUND_MODE,
    SUPPORT_PLAY_MEDIA,
    SUPPORT_PLAY,
    SUPPORT_PAUSE,
    SUPPORT_SEEK,
    SUPPORT_CLEAR_PLAYLIST,
    SUPPORT_SHUFFLE_SET,
    SUPPORT_REPEAT_SET,
    SUPPORT_NEXT_TRACK,
    SUPPORT_PREVIOUS_TRACK
)
from homeassistant.const import (
    CONF_TOKEN, 
    CONF_URL,
    CONF_NAME,
    STATE_OFF, 
    STATE_ON, 
    STATE_PLAYING, 
    STATE_PAUSED,
    STATE_UNAVAILABLE
)

from .browse_media import async_browse_media
from .player.websocket import MediaPlayerWebSocket
from .cloud_music import CloudMusic

from .manifest import manifest
DOMAIN = manifest.domain

_LOGGER = logging.getLogger(__name__)

SUPPORT_FEATURES = SUPPORT_VOLUME_STEP | SUPPORT_VOLUME_MUTE | SUPPORT_VOLUME_SET | \
    SUPPORT_TURN_ON | SUPPORT_TURN_OFF | SUPPORT_SELECT_SOURCE | SUPPORT_SELECT_SOUND_MODE | \
    SUPPORT_PLAY_MEDIA | SUPPORT_PLAY | SUPPORT_PAUSE | SUPPORT_PREVIOUS_TRACK | SUPPORT_NEXT_TRACK | \
    SUPPORT_BROWSE_MEDIA | SUPPORT_SEEK | SUPPORT_CLEAR_PLAYLIST | SUPPORT_SHUFFLE_SET | SUPPORT_REPEAT_SET

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    data = entry.data
    api_url = data.get(CONF_URL)
    cloud_music = CloudMusic(api_url)
    media_player = CloudMusicMediaPlayer(hass, cloud_music, { **data, **entry.options })
    hass.data[DOMAIN] = media_player
    async_add_entities([ media_player ], True)

class CloudMusicMediaPlayer(MediaPlayerEntity):

    def __init__(self, hass, cloud_music, config):
        self.hass = hass
        self.config = config
        self._attributes = {}
        # fixed attribute
        self._attr_media_image_remotely_accessible = True
        self._attr_device_class = MediaPlayerDeviceClass.TV.value
        self._attr_supported_features = SUPPORT_FEATURES

        # default attribute
        self._attr_source_list = ['网页浏览器', 'MPD', 'Windows应用']
        self._attr_sound_mode_list = []
        self._attr_name = manifest.name
        self._attr_unique_id = manifest.documentation
        self._attr_state =  STATE_OFF
        self._attr_volume_level = 1
        
        # source media player
        self._player = MediaPlayerWebSocket(self)
        self.cloud_music = cloud_music
        if len(cloud_music.playlist) > 0:
            hass.async_create_task(self.async_load_music())
            self._attr_state =  STATE_PAUSED

    @property
    def device_info(self):
        return {
            'identifiers': {
                (DOMAIN, manifest.documentation)
            },
            'name': self.name,
            'manufacturer': 'shaonianzhentan',
            'model': 'CloudMusic',
            'sw_version': manifest.version
        }

    @property
    def extra_state_attributes(self):
        return self._attributes

    async def async_browse_media(self, media_content_type=None, media_content_id=None):
        return await async_browse_media(self, media_content_type, media_content_id)

    async def async_select_source(self, source):
        if self._attr_source_list.count(source) > 0:
            self._attr_source = source

    async def async_select_source_mode(self, mode):
        if self._attr_sound_mode_list.count(mode) > 0:
            self._attr_source_mode = mode

    async def async_turn_off(self):
        self._attr_state = STATE_OFF

    async def async_turn_on(self):
        self._attr_state = STATE_ON

    async def async_volume_up(self):
        print('声音大一点')
        await self._player.async_volume_up()

    async def async_volume_down(self):
        print('声音小一点')
        await self._player.async_volume_down()

    async def async_mute_volume(self, mute):
        await self._player.async_mute_volume(mute)

    async def async_set_volume_level(self, volume):
        print(f'声音调到{volume}')
        await self._player.async_set_volume_level(volume)

    async def async_play_media(self, media_type, media_id, **kwargs):
        print(media_type, media_id)
        if media_type == 'playlist':
            self.cloud_music.playindex = int(media_id)
            await self.async_load_music(True)
        else:
            await self._player.async_play_media(media_type, media_id)
        self._attr_state = STATE_PLAYING

    async def async_media_play(self):
        self._attr_state = STATE_PLAYING
        await self._player.async_media_play()

    async def async_media_pause(self):
        self._attr_state = STATE_PAUSED
        await self._player.async_media_pause()

    async def async_set_repeat(self, repeat):
        self._attr_repeat = repeat

    async def async_set_shuffle(self, shuffle):
        self._attr_shuffle = shuffle

    async def async_media_next_track(self):
        self._attr_state = STATE_PAUSED
        print('下一个')
        self.cloud_music.next()
        await self.async_load_music(True)

    async def async_media_previous_track(self):
        self._attr_state = STATE_PAUSED
        print('上一下')
        self.cloud_music.previous()
        await self.async_load_music(True)

    async def async_media_seek(self, position):
        await self._player.async_media_seek(position)

    async def async_media_stop(self):
        # 停止播放
        await self._player.async_media_stop()

    # 更新属性
    async def async_update(self):
        print('更新')

    # 加载音乐
    async def async_load_music(self, is_play=False):
        music_info = await self.cloud_music.async_music_info()
        if music_info is not None:
            self._attr_media_content_id = music_info.url
            self._attr_media_image_url = music_info.picUrl
            self._attr_media_album_name = music_info.album
            self._attr_media_title = music_info.song
            self._attr_media_artist = music_info.singer
            self._attr_app_id = self.cloud_music.playindex
            self._attr_app_name = music_info.singer
            # 播放音乐
            if is_play == True:
                await self.async_play_media(music_info.source, music_info.url)
        return music_info