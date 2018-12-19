import asyncio
from random import randint
from aiovk import ImplicitSession, API
from aiovk.longpoll import UserLongPoll

from typing import Tuple, Optional

from .message import TextMessage, StickerMessage, Message
from .event import EventType, T, long_poll_event_factory

class VkBot:
    _default_names = ('bot',)
    _default_scope = 'messages'

    def __init__(self, app_id: int, login: str, password: int,
                 names: Optional[Tuple[str]] = None,
                 scope: Optional[str] = None):
        self._id: Optional[int] = None
        self.app_id = app_id
        self.login: str = login
        self.password: str = password
        self.names: Tuple[str] = names or self._default_names
        self.scope: str = scope or self._default_scope
        self.session: ImplicitSession = None
        self.api: API = None
        self.long_poll: UserLongPoll = None
        self.messaging_task: asyncio.Task = None
        self.messages_queue: asyncio.Queue = asyncio.Queue()

    async def start(self) -> None:
        self.session = ImplicitSession(login=self.login,
                                       password=self.password,
                                       app_id=self.app_id,
                                       scope=self.scope)
        await self.session.authorize()
        self.api = API(self.session)
        self.long_poll = UserLongPoll(session_or_api=self.api,
                                      mode=2,
                                      version=3)
        self._id = await self.get_account_id()
        # self.create_handlers()
        self.messaging_task = asyncio.create_task(self.messenger())
        await self.listener()

    async def get_account_id(self) -> int:
        profile = await self.api.account.getProfileInfo()
        account = await self.api.utils.resolveScreenName(
            screen_name=profile.get('screen_name')
        )
        return account['object_id']

    async def send_text_message(self, peer_id: int, text: str):
        message = TextMessage(recipient_id=peer_id,
                              content=text)
        await self.messages_queue.put(message)

    async def send_sticker(self, peer_id: int, sticker_id: int):
        message = StickerMessage(recipient_id=peer_id,
                                 content=sticker_id)
        await self.messages_queue.put(message)

    async def process_message(self, message: Message):
        if type(message) == TextMessage:
            await self.api.messages.send(peer_id=message.recipient_id,
                                         random_id=randint(10000, 99999),
                                         message=message.content)
        elif type(message) == StickerMessage:
            await self.api.messages.send(peer_id=message.recipient_id,
                                         random_id=randint(10000, 99999),
                                         sticker_id=message.content)

    async def handle_long_poll_event(self,
                                     event_type: EventType,
                                     event: T):
        raise NotImplementedError

    async def listener(self):
        while True:
            response = await self.long_poll.wait()
            updates = response.get('updates', [])
            for update in updates:
                try:
                    event_type = EventType(update[0])
                except ValueError:
                    return
                event = long_poll_event_factory(*update)
                await self.handle_long_poll_event(event_type,
                                                  event)

    async def messenger(self):
        print('start messaging')
        while True:
            print('check queue')
            print(self.messages_queue.qsize())
            if not self.messages_queue.empty():
                message = await self.messages_queue.get()
                await self.process_message(message)
            await asyncio.sleep(1)