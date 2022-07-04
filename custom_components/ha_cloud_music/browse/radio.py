from urllib.parse import quote
from ..utils import parse_query
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

# 收藏的电台
async def radio_favorites(cloud_music, title, media_content_type):
    library_info = BrowseMedia(
        media_class=MEDIA_CLASS_DIRECTORY,
        media_content_id='',
        media_content_type=MEDIA_TYPE_PLAYLIST,
        title=title,
        can_play=False,
        can_expand=False,
        children=[],
    )
    res = await cloud_music.netease_cloud_music('/dj/sublist')
    for item in res['djRadios']:
        library_info.children.append(
            BrowseMedia(
                title=item.get('name'),
                media_class=MEDIA_CLASS_DIRECTORY,
                media_content_type=media_content_type,
                media_content_id=f"title={quote(item['name'])}&id={item['id']}",
                can_play=False,
                can_expand=True,
                thumbnail=cloud_music.netease_image_url(item['picUrl'])
            )
        )
    return library_info

# 电台音乐列表
async def radio_playlist(cloud_music, url_query):
    query = parse_query(url_query)
    title = query.get('title')
    id = query.get('id')
    # 电台详情列表
    library_info = BrowseMedia(
        media_class=MEDIA_CLASS_DIRECTORY,
        media_content_id=f"type=radio&id={id}&index=0",
        media_content_type=MEDIA_TYPE_PLAYLIST,
        title=title,
        can_play=True,
        can_expand=False,
        children=[],
    )
    playlist = await cloud_music.async_get_djradio(id)
    for index, music_info in enumerate(playlist):
        library_info.children.append(
            BrowseMedia(
                title=music_info.song,
                media_class=MEDIA_CLASS_MUSIC,
                media_content_type=MEDIA_TYPE_PLAYLIST,
                media_content_id=f"type=radio&id={id}&index={index}",
                can_play=True,
                can_expand=False,
                thumbnail=music_info.picUrl
            )
        )
    return library_info