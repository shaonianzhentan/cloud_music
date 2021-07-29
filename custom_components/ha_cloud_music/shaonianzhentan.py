import aiohttp
from urllib.parse import urlparse

# 获取HTTP请求信息
async def fetch_info(url):
    p = urlparse(url)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
        'Referer': f'{p.scheme}//{p.netloc}'
    }
    connector = aiohttp.TCPConnector(verify_ssl=False)
    async with aiohttp.ClientSession(headers=headers,connector=connector) as session:
        async with session.get(url) as response:
            return {
              'status': response.status,
              'url': str(response.url)
            }