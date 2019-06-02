import asyncio
import async_timeout

from pubmarine import PubPen
from sanic import Sanic
from sanic.request import Request
from sanic.response import json
from sanic.websocket import WebSocketProtocol, ConnectionClosed, WebSocketCommonProtocol
from util import arp
from db import sqlite
from api import admin_api
import ujson

from websocket import make_reply

app = Sanic()
app.event: PubPen


@app.listener('before_server_start')
async def setup_db(_app, loop):
    await sqlite.make_table()
    _app.event = PubPen(loop)


@app.route("/")
async def test(request):
    return json({"hello": "world"})


@app.websocket('/websocket/')
async def start_websocket(request, ws: WebSocketCommonProtocol):
    ws.mac = None
    await set_user(request, ws)

    def recv_msg(_data: dict):
        app.loop.create_task(ws.send(ujson.dumps(_data)))

    app.event.subscribe('chat', recv_msg)

    async def communicate():
        while True:
            async with async_timeout.timeout(10.0):
                data = await ws.recv()
            if data == 'ping':
                await asyncio.sleep(0)
                continue
            print('Received: ' + data)
            reply = await make_reply(data, request, ws, app.event)
            print('Sending: {}'.format(reply))
            async with async_timeout.timeout(10.0):
                await ws.send(reply)

    try:
        await communicate()

    except (ConnectionClosed, asyncio.TimeoutError, asyncio.base_futures.InvalidStateError):
        print('ConnectionClosed')
        await websocket_closed(request, ws)


async def set_user(request: Request, ws):
    ws.mac = await arp.get_mac_address_in_thread(request.ip)
    print(ws.mac)


async def websocket_closed(request, ws):
    print('closed')
    if ws.mac:
        await asyncio.gather(admin_api.delete_user(ws.mac), sqlite.disable_user(ws.mac))


@app.route("/users/<user_id>")
def chat_from_admin(request: Request, user_id):
    data = request.json
    print(data)
    return ''


if __name__ == "__main__":
    _loop = asyncio.ProactorEventLoop()
    asyncio.set_event_loop(_loop)
    app.run(host="0.0.0.0", port=8080, protocol=WebSocketProtocol)
