"""Add support for the Xiaomi TVs."""
import logging, time, datetime

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.storage import STORAGE_DIR
from homeassistant.components.media_player import MediaPlayerEntity
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
    SUPPORT_NEXT_TRACK,
    SUPPORT_PREVIOUS_TRACK
)
from homeassistant.const import (
    CONF_TOKEN, 
    CONF_NAME,
    STATE_OFF, 
    STATE_ON, 
    STATE_PLAYING, 
    STATE_PAUSED,
    STATE_UNAVAILABLE
)

from .manifest import manifest
DOMAIN = manifest.domain

_LOGGER = logging.getLogger(__name__)

SUPPORT_FEATURES = SUPPORT_VOLUME_STEP | SUPPORT_VOLUME_MUTE | SUPPORT_VOLUME_SET | \
    SUPPORT_TURN_ON | SUPPORT_TURN_OFF | SUPPORT_SELECT_SOURCE | SUPPORT_SELECT_SOUND_MODE | \
    SUPPORT_PLAY_MEDIA | SUPPORT_PLAY | SUPPORT_PAUSE | SUPPORT_PREVIOUS_TRACK | SUPPORT_NEXT_TRACK | \
    SUPPORT_BROWSE_MEDIA

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    entities = [
        CloudMusicMediaPlayer(hass)
    ]
    async_add_entities(entities, True)

class CloudMusicMediaPlayer(MediaPlayerEntity):

    def __init__(self, hass):
        self.hass = hass
        self._attr_unique_id = manifest.documentation
        self._state =  STATE_OFF
        self._attributes = {}

    @property
    def name(self):
        return manifest.name

    @property
    def volume_level(self):
        return 0.5

    @property
    def is_volume_muted(self):
        return False

    @property
    def state(self):
        return self._state

    @property
    def assumed_state(self):
        return True

    @property
    def sound_mode_list(self):
        return []

    @property
    def source_list(self):
        return []

    @property
    def media_duration(self):
        return 0

    @property
    def media_position(self):
        return 0

    @property
    def supported_features(self):
        """Flag media player features that are supported."""
        return SUPPORT_FEATURES

    @property
    def device_class(self):
        return 'tv'

    @property
    def device_info(self):
        return {
            'identifiers': {
                (DOMAIN, manifest.documentation)
            },
            'name': self.name,
            'manufacturer': 'shaonianzhentan',
            'model': 'CloudMusic',
            'sw_version': manifest.version,
            # "via_device": (DOMAIN, manifest.version)
        }

    @property
    def extra_state_attributes(self):
        return self._attributes

    async def async_browse_media(self, media_content_type=None, media_content_id=None):
        return []

    # 选择应用
    async def async_select_source(self, source):
        pass

    # 选择数据源
    async def async_select_source_mode(self, mode):
        pass

    async def async_turn_off(self):
        print('小度小度')

    async def async_turn_on(self):
        pass

    async def async_volume_up(self):
        print('声音大一点')

    async def async_volume_down(self):
        print('声音小一点')

    async def async_mute_volume(self, mute):
        pass

    async def async_set_volume_level(self, volume):
        print(f'声音调到{volume * 100}')

    async def async_play_media(self, media_type, media_id, **kwargs):
        # print(media_id)
        pass

    async def async_media_play(self):
        print('播放')

    async def async_media_pause(self):
        print('暂停')

    async def async_media_next_track(self):
        print('下一个')

    async def async_media_previous_track(self):
        print('上一下')

    # 更新属性
    async def async_update(self):
        print('更新')