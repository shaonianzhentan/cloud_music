import json, aiohttp
from urllib.parse import urlparse

# 全局请求头
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}

# 获取cookie
async def http_cookie(url):
    COOKIES = {'os': 'osx'}
    jar = aiohttp.CookieJar(unsafe=True)
    location = urlparse(url)
    location_orgin = f'{location.scheme}://{location.netloc}'
    print(location_orgin)
    async with aiohttp.ClientSession(headers=HEADERS, cookies=COOKIES, cookie_jar=jar) as session:
            async with session.get(url) as resp:
                cookies = session.cookie_jar.filter_cookies(location_orgin)
                for key, cookie in cookies.items():
                    COOKIES[key] = cookie.value
                result = await resp.json()
                return {
                    'cookie': COOKIES,
                    'data': result
                }

async def http_get(url, COOKIES={}):
    print(url)
    headers = {'Referer': url, **HEADERS}
    jar = aiohttp.CookieJar(unsafe=True)
    async with aiohttp.ClientSession(headers=headers, cookies=COOKIES, cookie_jar=jar) as session:
        async with session.get(url) as resp:
            result = await resp.json()
            return result

async def http_code(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return response.status