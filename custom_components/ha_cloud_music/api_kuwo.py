import aiohttp, json, re, os, uuid, math, urllib, threading, re
import http.cookiejar as HC
from .shaonianzhentan import fetch_info

import  requests
import json
from urllib.parse import quote as urlencode
from .kwDES import base64_encrypt
import time


###################### 获取酷我音乐 ######################
# 获取网易云 检测是否可用 
async def check_163_song_url( id, songName, singerName, url):
    print('url:', url)
    #if url is not None:
    # and not url.startswith('https://music.163.com/song/media/outer/url'):
    #    return url
    # 请求网页
    res = await fetch_info(url)
    result_url = res['url']
    if result_url == 'https://music.163.com/404':
        return None
    return url
    #return await search_kuwo_music_by_keyword(id, songName, singerName)
    '''
    check = await self.get('/check/music?id=' + str(id))
    print('check/music:', check)
    if check['success']:
        return url
    else:
        url = await search_kuwo_music_by_keyword(id, songName, singerName)
    return url
    '''

## mobile 方法获取播放歌曲，获取flac,mp3
async def get_kuwo_music_url( kuwo_musicid):
    try:
        mobi_url = 'http://mobi.kuwo.cn/mobi.s?f=kuwo&q=%s' % base64_encrypt('corp=kuwo&p2p=1&' + 'type=convert_url2&sig=0&format=mp3&rid=%s' % kuwo_musicid)
        #res = requests.get(url=mobi_url)
        connector = aiohttp.TCPConnector(verify_ssl=False)
        async with aiohttp.ClientSession(connector=connector) as session2:
            async with session2.get(mobi_url) as resp:
                result =  await resp.text()
                #print('在酷我音乐时，搜索到数据', str(result))
                song_url = re.findall('http[^\s$"]+', str(result))[0]
                #print('在酷我音乐song_url：', song_url)
                return song_url
    except Exception as e:
        print('在酷我音乐时，搜索时出现错误get_kuwo_music_url：' , e)
    return None

# pc 方法获取播放歌曲，只能获取320k 的mp3 ,无法获取flac.{'code': 200, 'msg': 'success', 'url': 'https://gs-sycdn.kuwo.cn/184e56121b301f9e9d7113e024c7c346/60d70a18/resource/n1/72/83/4273952263.mp3'}
async def get_kuwo_music_url_pc( kuwo_musicid):
    try:
        base_url = 'http://www.kuwo.cn/url'
        params = {
            'format': 'mp3',
            'rid': kuwo_musicid,
            'response': 'url',
            'type': 'convert_url3',
            'br': '320kmp3',  # 320K 代表是无陨音质。
            'from': 'web',
            't': str(int(time.time() * 1000)),
            'httpsStatus': '1'
        }
        headers = {
            'Connection': 'keep-alive',
            'Host': 'www.kuwo.cn',
            'Referer': 'http://www.kuwo.cn/search/list',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
        }
        connector = aiohttp.TCPConnector(verify_ssl=False)
        async with aiohttp.ClientSession(headers=headers, connector=connector) as session:
            async with session.get(base_url,params=params) as resp:
                resp_song =  await resp.text()
                song_info = json.loads(resp_song)
                #print('在酷我音乐song_url3：', song_info)
                song_url = song_info.get("url")
                return song_url
    except Exception as e:
        print('在酷我音乐时，搜索时出现错误get_kuwo_music_url：' , e)
    return None

async def search_kuwo_music_by_keyword( itemId, songName, singerName):
    default_url = "https://music.163.com/song/media/outer/url?id=" + str(itemId)+ ".mp3",
    try:
        # 如果含有特殊字符，则直接使用名称搜索
        searchObj = re.search(r'\(|（|：|:《', songName, re.M|re.I)
        if searchObj:
            keywords = songName
        else:    
            keywords = songName + ' - '+ singerName
        keyword = urllib.parse.quote(keywords)
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}
        url_list = 'http://kuwo.cn/search/list?key={}'.format(keyword)
        url_search_info =  'http://www.kuwo.cn/api/www/search/searchMusicBykeyWord?key=%s&pn=1&rn=1' % keyword
        search_token = ""
        headers = {
            'Connection': 'keep-alive',
            'Host': 'www.kuwo.cn',
            'Referer': 'http://www.kuwo.cn/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
        }
        #url_list = 'http://kuwo.cn/search/list?key={}'.format(keyword)
        url_list = 'http://www.kuwo.cn/'
        url_search_info = 'http://www.kuwo.cn/api/www/search/searchMusicBykeyWord?key=%s&pn=1&rn=1' % keyword
        connector = aiohttp.TCPConnector(verify_ssl=False)
        async with aiohttp.ClientSession(headers=headers, connector=connector) as session:
            async with session.get(url_list) as resp:
                cookies =  resp.cookies
                for key, cookie in cookies.items():
                    if key == 'kw_token':
                        search_token = cookie.value
                print('酷我音乐，kw_token ：%s ', search_token)
                if search_token == "" :
                    print('酷我音乐，kw_token 获取失败 ')
                    return None
            search_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36', 'referer': url_list, 'csrf': search_token}
            async with session.get(url_search_info, headers=search_headers) as res:
                res_text = await res.text()
                search_info = json.loads(json.loads(json.dumps(res_text)))
                #print(search_info)
                if (search_info['code'] != 200) or (int(search_info['data']['total'])) < 1 :
                        print('酷我音乐，kw_token 获取失败 ')
                        print('酷我音乐，无数据: %s',search_info)
                else:
                    kuwo_musicid = search_info['data']['list'][0]['musicrid'].replace('MUSIC_', '')
                    mobi_url = 'http://mobi.kuwo.cn/mobi.s?f=kuwo&q=%s' % base64_encrypt('corp=kuwo&p2p=1&' + 'type=convert_url2&sig=0&format=flac|mp3&rid=%s' % kuwo_musicid)
                    # 两种方式获取URL
                    #song_url = await get_kuwo_music_url(kuwo_musicid )
                    song_url = await get_kuwo_music_url_pc(kuwo_musicid )
                    return song_url
    except Exception as e:
        print('在酷我音乐时，搜索时出现错误search_kuwo_music_by_keyword：', e)
    return default_url
