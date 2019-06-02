import asyncio
from urllib.parse import urljoin

import aiohttp

import constant

host = constant.admin_host


async def send_user_info(data: dict):
    gps = data.get('gps')
    if not gps:
        gps = '37.495470,127.038855'
    lat, log = gps.split(',')

    data = {'Users': {'battery': data.get('battery'), 'connectedHost': data.get('connected_host'),
                      'groupId': constant.group_id, 'hpno': data.get('id'), 'latitude': lat, 'logitude': log,
                      'myHost': data.get('my_host'), 'online': data.get('is_online')}}
    async with aiohttp.ClientSession() as session:
        async with session.post(urljoin(host, '/users'),
                                json=data) as response:
            print(await response.text())


async def delete_user(user_id):
    async with aiohttp.ClientSession() as session:
        async with session.post(urljoin(host, '/users/{}/delete'.format(user_id))) as response:
            print(await response.text())


if __name__ == '__main__':
    loop = asyncio.get_event_loop().run_until_complete(send_user_info({
        "type": "update",
        "sequence_id": "ff70a4cd231",
        "id": "01050282038",
        "battery": 100,
        "my_host": "192.168.0.1",
        "connected_host": "192.168.100.12",
        "is_online": False,
        "gps": "37.495470,127.038855"
    }))
