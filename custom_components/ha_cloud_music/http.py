import os
from homeassistant.components.http import HomeAssistantView
from .manifest import manifest
from .http_api import http_get

DOMAIN = manifest.domain

class HttpView(HomeAssistantView):

    url = f"/{DOMAIN}-api"
    name = DOMAIN
    requires_auth = True

    async def get(self, request):
        hass = request.app["hass"]
        cloud_music = hass.data[DOMAIN].cloud_music
        query = request.query
        api = query.get('api')
        data = await http_get(cloud_music.api_url + api, cloud_music.cookie)
        return self.json(data)

    async def delete(self, request):
        hass = request.app["hass"]
        query = request.query
        return self.json({ 'code': 0, 'msg': '删除成功'})

    async def put(self, request):
        hass = request.app["hass"]
        query = request.query
        return self.json({ 'code': 0, 'msg': '创建成功'})

    async def post(self, request):
        hass = request.app["hass"]
        media_player = hass.data[DOMAIN]
        cloud_music = media_player.cloud_music

        body = await request.json()
        id = body.get('id')
        act = body.get('act')
        playindex = body.get('index', 0)
        if act == 'playlist':
            await cloud_music.async_load_playlist(id, playindex)
            await media_player.async_load_music(True)
            return self.json({ 'code': 0, 'msg': '正在播放歌单'})

        return self.json({ 'code': 0, 'msg': '保存成功'})