from collections import defaultdict
from random import randint
from aiovk import API, ImplicitSession
from aiovk.longpoll import LongPoll
import os

if 'HEROKU_APP' in os.environ:
    app_id = int(os.environ.get('APP_ID', 0))
else:
    import local_settings
    app_id = local_settings.APP_ID


class NotConferenceException(Exception):
    pass


class Bot2:
    STATUSES = {
        'UNREAD':       1,
        'REPLIED':      4,
        'IMPORTANT':    8,
        'CHAT':         16,
        'FRIENDS':      32,
        'SPAM':         64,
        'DELЕTЕD':      128,
        'FIXED':        256,
        'MEDIA':        512,
        'CONF':         8192,
        'HIDDEN':       65536
    }

    INCOMING = 0
    OUTCOMING = 1
    OUTBOX = 2

    CONF_PEER_MODIFIER = 2000000000

    _id = None
    _session = None
    _api = None
    _loop_started = None
    _handlers = {
        INCOMING: defaultdict(list),
        OUTCOMING: defaultdict(list)
    }

    def __init__(self, login, password):
        self.login = login
        self.password = password
        self.is_cheating = False

    @staticmethod
    async def create(login, password):
        bot = Bot2(login, password)
        await bot.auth()
        return bot

    @staticmethod
    def _format_message(message):
        return {
            'status': message[2],
            'sender': message[3],
            'message': message[6]
        }

    def get_chat_id_by_peer_id(self, peer_id):
        if peer_id < self.CONF_PEER_MODIFIER:
            raise NotConferenceException
        return peer_id - self.CONF_PEER_MODIFIER

    def cheat_switch(self):
        self.is_cheating = not self.is_cheating

    async def set_account_id(self):
        self._id = (await self._api.utils.resolveScreenName(
            screen_name=(await self._api.account.getProfileInfo()).get(
                'screen_name'
            ))).get('object_id')

    def get_account_id(self):
        return self._id

    async def auth(self):
        self._session = ImplicitSession(self.login,
                                        self.password,
                                        app_id,
                                        scope='messages')
        await self._session.authorize()
        self._api = API(self._session)
        await self.set_account_id()

    def add_handler(self,
                    handler,
                    message_type=STATUSES['UNREAD'],
                    direction=INCOMING):
        self._handlers[direction][message_type].append(handler)

    async def handle_message(self, message):
        _handlers = self._handlers[self.OUTCOMING] \
            if message['status'] & self.OUTBOX \
            else self._handlers[self.INCOMING]

        for status, bitmask in self.STATUSES.items():
            if bitmask & message['status']:
                for handler in _handlers[bitmask]:
                    await handler(message)

    async def send_message(self, recepient_id, message=''):
        await self._api.messages.send(peer_id=recepient_id,
                                      random_id=randint(10000, 99999),
                                      message=message)

    async def send_answer(self, message, answer):
        await self.send_message(recepient_id=message['sender'],
                                message=answer)

    async def send_sticker(self, send_to, sticker_id):
        await self._api.messages.sendSticker(peer_id=send_to,
                                             random_id=randint(10000, 99999),
                                             sticker_id=sticker_id)

    async def get_chat_users(self, peer_id):
        return await self._api.messages.getChatUsers(
            chat_id=self.get_chat_id_by_peer_id(peer_id),
            fields='first_name, last_name'
        )

    async def start(self):
        self._loop_started = True
        _poll = LongPoll(self._api, mode=2)
        while self._loop_started:
            response = await _poll.wait()
            if not 'HEROKU_APP' in os.environ:
                print(response)
            for update in response.get('updates', []):
                if update[0] == 4:
                    await self.handle_message(self._format_message(update))

    def stop(self):
        self._loop_started = False
