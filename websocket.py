import traceback
import uuid

import pubmarine
import ujson

import constant
from db.sqlite import update_or_insert_user_info, get_all_user_info


async def make_reply(msg: str, *args) -> str:
    message: Message = Message()

    try:
        data: dict = ujson.loads(msg)
    except ValueError:
        return await message.get_reply()

    _args = [data, *args]

    if data.get('type') == 'query':
        if data.get('query_type') == 'info':
            message = GroupInfo(*_args)
    elif data.get('type') == 'update':
        message = UpdateInfo(*_args)
    elif data.get('type') == 'msg':
        message = Chat(*_args)
    elif data.get('type') == 'client_info':
        message = ClientInfo(*_args)

    return await message.get_reply()


class Message:
    input_data: dict = None
    sequence_id: str or None = None
    _reply: dict = None
    is_generated = False

    def __init__(self, input_data: dict = None, request=None, ws=None, event=None):
        self.ws = ws
        self.request = request
        self.input_data = input_data
        self.event: pubmarine.PubPen = event

        if input_data:
            self.sequence_id = self.input_data.get('sequence_id')

    async def generate_reply(self):
        pass

    async def get_reply(self):
        try:
            if not self.is_generated:
                await self.generate_reply()
                if self._reply and self.sequence_id and not self._reply.get('sequence_id'):
                    self._reply.update({'sequence_id': self.sequence_id})
                self.is_generated = True

            if self._reply:
                return ujson.dumps(self._reply)

            return '{"error": "invalid message"}'
        except:
            traceback.print_exc()

        return '{"sequence_id": {}, "status":"fail"}'.format(str(self.sequence_id))

    @property
    def reply(self):
        raise Exception('Please `await get_reply()`')

    @reply.setter
    def reply(self, new_reply):
        self._reply = new_reply


class GroupInfo(Message):
    async def generate_reply(self):
        users = await get_all_user_info()
        self.reply = {"group": {"group_id": constant.group_id, "number": len(users)},
                      "users": users}


class UpdateInfo(Message):
    async def generate_reply(self):
        await update_or_insert_user_info(self.input_data)
        self.reply = {'status': "ok"}


class Chat(Message):
    async def generate_reply(self):
        self.reply = {'status': "ok"}

        chat_data = dict(self.input_data)
        chat_data['sequence_id'] = str(uuid.uuid4())
        chat_data['from'] = self.ws.mac
        chat_data.pop('target')
        self.event.publish('chat', chat_data)


class ClientInfo(Message):
    async def generate_reply(self):
        self.reply = {
            "mac": self.ws.mac,
            "connected_host": "192.168.0.152:8080"
        }
