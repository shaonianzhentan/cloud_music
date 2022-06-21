"""Support for media browsing."""
import logging, os
from homeassistant.helpers.network import get_url
from homeassistant.components.media_player import BrowseError, BrowseMedia
from homeassistant.components.media_player.const import (
    MEDIA_CLASS_ALBUM,
    MEDIA_CLASS_ARTIST,
    MEDIA_CLASS_CHANNEL,
    MEDIA_CLASS_DIRECTORY,
    MEDIA_CLASS_EPISODE,
    MEDIA_CLASS_MOVIE,
    MEDIA_CLASS_MUSIC,
    MEDIA_CLASS_PLAYLIST,
    MEDIA_CLASS_SEASON,
    MEDIA_CLASS_TRACK,
    MEDIA_CLASS_TV_SHOW,
    MEDIA_TYPE_ALBUM,
    MEDIA_TYPE_ARTIST,
    MEDIA_TYPE_CHANNEL,
    MEDIA_TYPE_EPISODE,
    MEDIA_TYPE_MOVIE,
    MEDIA_TYPE_PLAYLIST,
    MEDIA_TYPE_SEASON,
    MEDIA_TYPE_TRACK,
    MEDIA_TYPE_TVSHOW,
)

PLAYABLE_MEDIA_TYPES = [
    MEDIA_TYPE_ALBUM,
    MEDIA_TYPE_ARTIST,
    MEDIA_TYPE_TRACK,
]

CONTAINER_TYPES_SPECIFIC_MEDIA_CLASS = {
    MEDIA_TYPE_ALBUM: MEDIA_CLASS_ALBUM,
    MEDIA_TYPE_ARTIST: MEDIA_CLASS_ARTIST,
    MEDIA_TYPE_PLAYLIST: MEDIA_CLASS_PLAYLIST,
    MEDIA_TYPE_SEASON: MEDIA_CLASS_SEASON,
    MEDIA_TYPE_TVSHOW: MEDIA_CLASS_TV_SHOW,
}

CHILD_TYPE_MEDIA_CLASS = {
    MEDIA_TYPE_SEASON: MEDIA_CLASS_SEASON,
    MEDIA_TYPE_ALBUM: MEDIA_CLASS_ALBUM,
    MEDIA_TYPE_ARTIST: MEDIA_CLASS_ARTIST,
    MEDIA_TYPE_MOVIE: MEDIA_CLASS_MOVIE,
    MEDIA_TYPE_PLAYLIST: MEDIA_CLASS_PLAYLIST,
    MEDIA_TYPE_TRACK: MEDIA_CLASS_TRACK,
    MEDIA_TYPE_TVSHOW: MEDIA_CLASS_TV_SHOW,
    MEDIA_TYPE_CHANNEL: MEDIA_CLASS_CHANNEL,
    MEDIA_TYPE_EPISODE: MEDIA_CLASS_EPISODE,
}

_LOGGER = logging.getLogger(__name__)

async def async_browse_media(media_player, media_content_type, media_content_id):
    # 主界面
    if media_content_type in [None, 'home']:
        library_info = BrowseMedia(
            media_class=MEDIA_CLASS_DIRECTORY,
            media_content_id="home",
            media_content_type="home",
            title="云音乐",
            can_play=False,
            can_expand=True,
            children=[],
        )
        # 分组列表
        library_info.children.append(
            BrowseMedia(
                title='音乐列表',
                media_class=MEDIA_CLASS_DIRECTORY,
                media_content_type="playlist",
                media_content_id='playlist',
                can_play=False,
                can_expand=True,
                thumbnail="https://p2.music.126.net/fL9ORyu0e777lppGU3D89A==/109951167206009876.jpg?param=500y500"
            )
        )
    elif media_content_type == 'playlist':
        library_info = BrowseMedia(
            media_class=MEDIA_CLASS_DIRECTORY,
            media_content_id=media_content_id,
            media_content_type=media_content_type,
            title='音乐列表',
            can_play=False,
            can_expand=False,
            children=[],
        )
        # 播放列表
        playlist = media_player.cloud_music.playlist
        for index, item in enumerate(playlist):
            library_info.children.append(
                BrowseMedia(
                    title=f'{item.song} - {item.singer}',
                    media_class=MEDIA_CLASS_MUSIC,
                    media_content_type="playlist",
                    media_content_id=index,
                    can_play=True,
                    can_expand=False,
                    thumbnail=item.picUrl
                )
            )
    return library_info