import asyncio, aiohttp, json
from urllib.parse import urlparse

# 获取HTTP内容
async def fetch_text(url, headers = {}):
    p = urlparse(url)
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
        'Referer': f'{p.scheme}//{p.netloc}'
    }
    HEADERS.UPDATE(headers)
    text = None
    connector = aiohttp.TCPConnector(verify_ssl=False)
    async with aiohttp.ClientSession(headers=HEADERS, connector=connector) as session:
        async with session.get(url) as resp:
            text = await resp.text()
    return text

# 获取HTTP内容JSON格式
async def fetch_json(url, headers = {}):
    text = await fetch_text(url, headers)
    result = {}
    if text is not None:
        result = json.loads(text)
    return result

# 获取HTTP请求信息
async def fetch_info(url):
    p = urlparse(url)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
        'Referer': f'{p.scheme}//{p.netloc}'
    }
    connector = aiohttp.TCPConnector(verify_ssl=False)
    async with aiohttp.ClientSession(headers=headers, connector=connector) as session:
        async with session.get(url) as response:
            return {
              'status': response.status,
              'url': str(response.url)
            }

# 执行异步方法
def async_create_task(async_func):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(async_func)