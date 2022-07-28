"""Support for media browsing."""
import logging, os
from urllib.parse import urlparse, parse_qs, parse_qsl, quote
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

from .browse.radio import radio_favorites, radio_playlist
from .browse.playlist import playlist_all, playlist_toplist, playlist_recommend_resource, playlist_daily, user_playlist
from .browse.artists import artists_favorites, artists_playlist

async def async_browse_media(media_player, media_content_type, media_content_id):
    cloud_music = media_player.cloud_music
    # 主界面
    if media_content_type in [None, 'home']:
        children = [
            {
                'title': '播放列表',
                'type': 'playlist',
                'thumbnail': 'https://p2.music.126.net/fL9ORyu0e777lppGU3D89A==/109951167206009876.jpg'
            },{
                'title': '推荐歌曲',
                'type': 'daily',
                'thumbnail': 'http://p3.music.126.net/ik8RFcDiRNSV2wvmTnrcbA==/3435973851857038.jpg'
            },{
                'title': '推荐歌单',
                'type': 'recommend_resource',
                'thumbnail': 'http://p3.music.126.net/ik8RFcDiRNSV2wvmTnrcbA==/3435973851857038.jpg'
            },{
                'title': '我的云盘',
                'type': 'cloud',
                'thumbnail': 'http://p3.music.126.net/ik8RFcDiRNSV2wvmTnrcbA==/3435973851857038.jpg'
            },{
                'title': '我的歌单',
                'type': 'created',
                'thumbnail': 'https://p2.music.126.net/ElBQCbIDRire6yg0ptVfJQ==/109951164152032144.jpg'
            },{
                'title': '我的电台',
                'type': 'radio',
                'thumbnail': 'http://p1.music.126.net/6nuYK0CVBFE3aslWtsmCkQ==/109951165472872790.jpg'
            },{
                'title': '我的歌手',
                'type': 'artist',
                'thumbnail': 'http://p1.music.126.net/9M-U5gX1gccbuBXZ6JnTUg==/109951165264087991.jpg'
            },{
                'title': '榜单',
                'type': 'toplist',
                'thumbnail': 'http://p2.music.126.net/pcYHpMkdC69VVvWiynNklA==/109951166952713766.jpg'
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
            library_info.children.append(
                BrowseMedia(
                    title=item['title'],
                    media_class=MEDIA_CLASS_DIRECTORY,
                    media_content_type=item['type'],
                    media_content_id=item['title'],
                    can_play=False,
                    can_expand=True,
                    thumbnail=cloud_music.netease_image_url(item['thumbnail'])
                )
            )
    elif media_content_type == 'playlist':
        library_info = BrowseMedia(
            media_class=MEDIA_CLASS_DIRECTORY,
            media_content_id=media_content_id,
            media_content_type=MEDIA_TYPE_PLAYLIST,
            title=media_content_id,
            can_play=False,
            can_expand=False,
            children=[],
        )
        playlist = cloud_music.playlist
        for index, item in enumerate(playlist):
            title = item.song
            if not item.singer:
                title = f'{title} - {item.singer}'
            library_info.children.append(
                BrowseMedia(
                    title=title,
                    media_class=MEDIA_CLASS_MUSIC,
                    media_content_type=MEDIA_TYPE_PLAYLIST,
                    media_content_id=f"type=index&index={index}",
                    can_play=True,
                    can_expand=False,
                    thumbnail=item.thumbnail
                )
            )
    elif media_content_type == 'daily':
        library_info = BrowseMedia(
            media_class=MEDIA_CLASS_DIRECTORY,
            media_content_id=f"type=daily&index=0",
            media_content_type=MEDIA_TYPE_PLAYLIST,
            title=media_content_id,
            can_play=True,
            can_expand=False,
            children=[],
        )
        playlist = await cloud_music.async_get_dailySongs()
        for index, music_info in enumerate(playlist):
            library_info.children.append(
                BrowseMedia(
                    title=music_info.song,
                    media_class=MEDIA_CLASS_MUSIC,
                    media_content_type=MEDIA_TYPE_PLAYLIST,
                    media_content_id=f"type=daily&index={index}",
                    can_play=True,
                    can_expand=False,
                    thumbnail=music_info.thumbnail
                )
            )
    elif media_content_type == 'cloud':
        library_info = BrowseMedia(
            media_class=MEDIA_CLASS_DIRECTORY,
            media_content_id=f"type=cloud&index=0",
            media_content_type=MEDIA_TYPE_PLAYLIST,
            title=media_content_id,
            can_play=True,
            can_expand=False,
            children=[],
        )
        playlist = await cloud_music.async_get_cloud()
        for index, music_info in enumerate(playlist):
            library_info.children.append(
                BrowseMedia(
                    title=music_info.song,
                    media_class=MEDIA_CLASS_MUSIC,
                    media_content_type=MEDIA_TYPE_PLAYLIST,
                    media_content_id=f"type=cloud&index={index}",
                    can_play=True,
                    can_expand=False,
                    thumbnail=music_info.thumbnail
                )
            )
    elif media_content_type == 'created':
        return await user_playlist(cloud_music, media_content_id, 'all')
    elif media_content_type == 'radio':
        return await radio_favorites(cloud_music, media_content_id, 'radio-playlist')
    elif media_content_type == 'radio-playlist':
        return await radio_playlist(cloud_music, media_content_id)
    elif media_content_type == 'artist':
        return await artists_favorites(cloud_music, media_content_id, 'artist-playlist')
    elif media_content_type == 'artist-playlist':
        return await artists_playlist(cloud_music, media_content_id)
    elif media_content_type == 'toplist':
        return await playlist_toplist(cloud_music, media_content_id, 'all')
    elif media_content_type == 'recommend_resource':
        return await playlist_recommend_resource(cloud_music, media_content_id, 'all')
    elif media_content_type == 'all':
        return await playlist_all(cloud_music, media_content_id)
    return library_info