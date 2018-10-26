import asyncio

from collections import defaultdict
from random import randint
from typing import List, Tuple, Dict, Callable, Set

from aiovk import ImplicitSession, API
from aiovk.longpoll import UserLongPoll

import core.handler as handlers

from .event import long_poll_event_factory, EventType, T
from .message import Message, TextMessage, StickerMessage

class VkBot:
    _default_names: Tuple[str] = ('bot',)

    _handler_types = {
        EventType.AddMessage: handlers.AddMessageHandler
    }

    def __init__(self, app_id: int,
                 login: str,
                 password: str,
                 names: Tuple[str]=None,
                 scope: str='messages') -> None:
        self._id: int = None
        self.app_id:int = app_id
        self.login: str = login
        self.password: str = password
        self.names: Tuple[str] = names or self._default_names
        self.scope: str = scope
        self.session: ImplicitSession = None
        self.api: API = None
        self.long_poll: UserLongPoll = None
        self.messaging_task: asyncio.Task = None
        self.messages_queue: asyncio.Queue = asyncio.Queue()
        self.handlers: Dict[EventType,
                            Set[handlers.BaseHandler]] = defaultdict(set)
        self.handlers_location = handlers



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
        self.create_handlers()
        self.messaging_task = asyncio.create_task(self.messenger())
        await self.listener()

    def create_handlers(self):
        for event_type, class_name in self._handler_types.items():
            for cls in class_name.__subclasses__():
                print('add handler', cls)
                handler = cls(self)
                self.handlers[event_type].add(handler)


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
                                          random_id=randint(10000,99999),
                                          message=message.content)
        elif type(message) == StickerMessage:
            await self.api.messages.send(peer_id=message.recipient_id,
                                                 random_id=randint(10000,99999),
                                                 sticker_id=message.content)

    async def handle_long_poll_event(self,
                                     event_type: EventType,
                                     event: T):
        if event_type in self.handlers:
            for handler in self.handlers[event_type]:
                await handler.handle(event)

    async def listener(self):
        while True:
            response = await self.long_poll.wait()
            updates = response.get('updates', [])
            for update in updates:
                print(update)
                try:
                    event_type = EventType(update[0])
                except ValueError:
                    event_type = None
                if event_type is not None:
                    event = long_poll_event_factory(*update)
                    await self.handle_long_poll_event(event_type,
                                                         event)

    async def messenger(self):
        print('start messeging')
        while True:
            # print('check queue')
            # print(self.messages_queue.qsize())
            if not self.messages_queue.empty():
                message = await self.messages_queue.get()
                await self.process_message(message)
            await asyncio.sleep(1)


