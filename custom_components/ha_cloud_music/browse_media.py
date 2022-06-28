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
        children = [
            {
                'title': '播放列表',
                'type': 'playlist',
                'can_play': True,
                'thumbnail': 'https://p2.music.126.net/fL9ORyu0e777lppGU3D89A==/109951167206009876.jpg?param=500y500'
            },{
                'title': '我的云盘',
                'type': 'cloud',
                'can_play': True,
                'thumbnail': 'http://p3.music.126.net/ik8RFcDiRNSV2wvmTnrcbA==/3435973851857038.jpg?param=500y500'
            },{
                'title': '创建的歌单',
                'type': 'created',
                'can_play': False,
                'thumbnail': 'https://p2.music.126.net/fL9ORyu0e777lppGU3D89A==/109951167206009876.jpg?param=500y500'
            },{
                'title': '收藏的歌单',
                'type': 'favorites',
                'can_play': False,
                'thumbnail': 'https://p2.music.126.net/fL9ORyu0e777lppGU3D89A==/109951167206009876.jpg?param=500y500'
            },{
                'title': '我的电台',
                'type': 'radio',
                'can_play': False,
                'thumbnail': 'http://p1.music.126.net/6nuYK0CVBFE3aslWtsmCkQ==/109951165472872790.jpg?param=500y500'
            },{
                'title': '我的歌手',
                'type': 'singer',
                'can_play': False,
                'thumbnail': 'http://p1.music.126.net/9M-U5gX1gccbuBXZ6JnTUg==/109951165264087991.jpg?param=500y500'
            },{
                'title': '云音乐特色榜',
                'type': 'feature',
                'can_play': False,
                'thumbnail': 'http://p2.music.126.net/pcYHpMkdC69VVvWiynNklA==/109951166952713766.jpg?param=500y500'
            },{
                'title': '全球媒体榜',
                'type': 'global',
                'can_play': False,
                'thumbnail': 'http://p1.music.126.net/G91csin09maPrNgqcUKnBQ==/109951165698553069.jpg?param=500y500'
            }
        ]
        library_info = BrowseMedia(
            media_class=MEDIA_CLASS_DIRECTORY,
            media_content_id="home",
            media_content_type="home",
            title="云音乐",
            can_play=False,
            can_expand=True,
            children=[],
        )
        for item in children:
            can_play = item['can_play']
            can_expand = can_play == False
            library_info.children.append(
                BrowseMedia(
                    title=item['title'],
                    media_class=MEDIA_CLASS_MUSIC,
                    media_content_type=item['type'],
                    media_content_id=item['title'],
                    can_play=can_play,
                    can_expand=can_expand,
                    thumbnail=item['thumbnail']
                )
            )
    elif media_content_type == 'playlist':
        library_info = BrowseMedia(
            media_class=MEDIA_CLASS_DIRECTORY,
            media_content_id=media_content_id,
            media_content_type=media_content_type,
            title=media_content_id,
            can_play=False,
            can_expand=False,
            children=[],
        )
        playlist = media_player.cloud_music.playlist
        for index, item in enumerate(playlist):
            library_info.children.append(
                BrowseMedia(
                    title=f'{item.song} - {item.singer}',
                    media_class=MEDIA_CLASS_MUSIC,
                    media_content_type=media_content_type,
                    media_content_id=index,
                    can_play=True,
                    can_expand=False,
                    thumbnail=item.picUrl
                )
            )
    elif media_content_type == 'cloud':
        library_info = BrowseMedia(
            media_class=MEDIA_CLASS_DIRECTORY,
            media_content_id=media_content_id,
            media_content_type=media_content_type,
            title=media_content_id,
            can_play=False,
            can_expand=False,
            children=[],
        )
    elif media_content_type == 'created':
        library_info = BrowseMedia(
            media_class=MEDIA_CLASS_DIRECTORY,
            media_content_id=media_content_id,
            media_content_type=media_content_type,
            title=media_content_id,
            can_play=False,
            can_expand=False,
            children=[],
        )
    elif media_content_type == 'favorites':
        library_info = BrowseMedia(
            media_class=MEDIA_CLASS_DIRECTORY,
            media_content_id=media_content_id,
            media_content_type=media_content_type,
            title=media_content_id,
            can_play=False,
            can_expand=False,
            children=[],
        )
    elif media_content_type == 'radio':
        library_info = BrowseMedia(
            media_class=MEDIA_CLASS_DIRECTORY,
            media_content_id=media_content_id,
            media_content_type=media_content_type,
            title=media_content_id,
            can_play=False,
            can_expand=False,
            children=[],
        )
    elif media_content_type == 'singer':
        library_info = BrowseMedia(
            media_class=MEDIA_CLASS_DIRECTORY,
            media_content_id=media_content_id,
            media_content_type=media_content_type,
            title=media_content_id,
            can_play=False,
            can_expand=False,
            children=[],
        )
    elif media_content_type == 'feature':
        library_info = BrowseMedia(
            media_class=MEDIA_CLASS_DIRECTORY,
            media_content_id=media_content_id,
            media_content_type=media_content_type,
            title=media_content_id,
            can_play=False,
            can_expand=False,
            children=[],
        )
    elif media_content_type == 'global':
        library_info = BrowseMedia(
            media_class=MEDIA_CLASS_DIRECTORY,
            media_content_id=media_content_id,
            media_content_type=media_content_type,
            title=media_content_id,
            can_play=False,
            can_expand=False,
            children=[],
        )
    return library_info