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
        cloud_music = hass.data[DOMAIN]
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
        cloud_music = hass.data[DOMAIN]
        body = request.json()
        id = body.get('id')
        act = body.get('act')
        if act == 'playlist':
            cloud_music.load_playlist(id)
            return self.json({ 'code': 0, 'msg': '正在播放歌单'})

        return self.json({ 'code': 0, 'msg': '保存成功'})