import aiohttp, uuid

from shaonianzhentan import async_create_task
# 乐听头条配置
UID = str(uuid.uuid4()).replace('-','')

class Test:
    def __init__(self) -> None:
        pass

    # 获取新闻
    async def _get_news(self, session, leting_headers, catalog_id):
        async with session.get('https://app.leting.io/app/url/channel?catalog_id=' + catalog_id \
            + '&size=20&distinct=1&v=v8&channel=huawei', headers=leting_headers) as res:
            r = await res.json()
            _list = r['data']['data']
            _newlist = map(lambda item: {
                "id": item['sid'],
                "name": item['title'],
                "album": item['catalog_name'],
                "image": item['source_icon'],
                "duration": item['duration'],
                "url": item['audio'],
                "song": item['title'],
                "singer": item['source']
                }, _list)
            return list(_newlist)
        return None

    async def play_news(self, name):        
        leting_headers = {"uid":UID, "logid": UID, "token": ''}
        async with aiohttp.ClientSession() as session:
            async with session.get('https://app.leting.io/app/auth?uid=' + UID \
                + '&appid=a435325b8662a4098f615a7d067fe7b8&ts=1628297581496&sign=4149682cf40c2bf2efcec8155c48b627&v=v9&channel=huawei', headers=leting_headers) as res:
                r = await res.json()
                print(r)
                leting_headers['token'] = r['data']['token']                
                _newlist = []
                # 热点
                _list = await self._get_news(session, leting_headers, 'f3f5a6d2-5557-4555-be8e-1da281f97c22')
                if _list is not None:
                    _newlist.extend(_list)
                # 社会
                _list = await self._get_news(session, leting_headers, 'd8e89746-1e66-47ad-8998-1a41ada3beee')
                if _list is not None:
                    _newlist.extend(_list)
                # 国际
                _list = await self._get_news(session, leting_headers, '4905d954-5a85-494a-bd8c-7bc3e1563299')
                if _list is not None:
                    _newlist.extend(_list)
                # 国内
                _list = await self._get_news(session, leting_headers, 'fc583bff-e803-44b6-873a-50743ce7a1e9')
                if _list is not None:
                    _newlist.extend(_list)
                # 科技
                _list = await self._get_news(session, leting_headers, 'f5cff467-2d78-4656-9b72-8e064c373874')
                if _list is not None:
                    _newlist.extend(_list)
                '''
                热点：f3f5a6d2-5557-4555-be8e-1da281f97c22
                社会：d8e89746-1e66-47ad-8998-1a41ada3beee
                国际：4905d954-5a85-494a-bd8c-7bc3e1563299
                国内：fc583bff-e803-44b6-873a-50743ce7a1e9
                体育：c7467c00-463d-4c93-b999-7bbfc86ec2d4
                娱乐：75564ed6-7b68-4922-b65b-859ea552422c
                财经：c6bc8af2-e1cc-4877-ac26-bac1e15e0aa9
                科技：f5cff467-2d78-4656-9b72-8e064c373874
                军事：ba89c581-7b16-4d25-a7ce-847a04bc9d91
                生活：40f31d9d-8af8-4b28-a773-2e8837924e2e
                教育：0dee077c-4956-41d3-878f-f2ab264dc379
                汽车：5c930af2-5c8a-4a12-9561-82c5e1c41e48
                人文：f463180f-7a49-415e-b884-c6832ba876f0
                旅游：8cae0497-4878-4de9-b3fe-30518e2b6a9f
                北京市：29d6168ed172c09fc81d2d71d4ec0686
                '''
                # 调用服务，执行播放
                print(_newlist)

t = Test()

async_create_task(t.play_news(''))