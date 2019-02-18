import asyncio
from collections import defaultdict
from random import randint
from aiovk import ImplicitSession, API
from aiovk.longpoll import UserLongPoll

from typing import Tuple, Optional, DefaultDict, Union, List

from .message import TextMessage, StickerMessage
from .handlers import InboxMessageHandler
from .event import DefaultLongPollEvent, EventType, NewMessageLongPollEvent, \
    MessageFlags, long_poll_event_factory
from .user import User


class NotConferenceException(Exception):
    pass


class VkBot:
    CONF_PEER_MODIFIER = 2000000000

    _default_names = ('bot',)
    _default_scope = 'messages'
    _handler_instances: DefaultDict[EventType, set] = defaultdict(set)

    handler_classes = {EventType.NewMessage: InboxMessageHandler}

    def __init__(self, app_id: int, login: str, password: str,
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
        self.messaging_task: Optional[asyncio.Task] = None
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
        await self.create_handlers()
        self.messaging_task = asyncio.create_task(self.messenger())
        await self.listener()

    async def create_handlers(self):
        for event_type, handler_class in self.handler_classes.items():
            for handler_subclass in handler_class.__subclasses__():
                self._handler_instances[event_type].add(
                    handler_subclass(self))

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
                                 sticker_id=sticker_id)
        await self.messages_queue.put(message)

    async def process_message(self, message: Union[TextMessage,
                                                   StickerMessage]):
        if isinstance(message, TextMessage):
            await self.api.messages.send(peer_id=message.recipient_id,
                                         random_id=randint(10000, 99999),
                                         message=message.content)
        elif isinstance(message, StickerMessage):
            await self.api.messages.send(peer_id=message.recipient_id,
                                         random_id=randint(10000, 99999),
                                         sticker_id=message.sticker_id)
        else:
            raise ValueError('unexpected type')

    async def get_chat_users(self, peer_id) -> List[User]:
        users_list = await self.api.messages.getConversationMembers(
            peer_id=peer_id,
            fields='first_name, last_name'
        )
        return [User(**user) for user in users_list.get('profiles')
                if user['id'] != self._id]

    async def handle_long_poll_event(self,
                                     event: Union[DefaultLongPollEvent,
                                                  NewMessageLongPollEvent]):
        if isinstance(event, NewMessageLongPollEvent):
            await self.process_new_message(event)
        else:
            pass

    async def process_new_message(self, event: NewMessageLongPollEvent):
        if MessageFlags.Outbox in event.flags:
            await self.process_outbox_message(event)
        else:
            print('inbox')
            await self.process_inbox_message(event)

    async def process_inbox_message(self, event: NewMessageLongPollEvent):
        print(event.text, self.names)
        if event.text.startswith(self.names):
            for _handler in self._handler_instances.get(EventType.NewMessage,
                                                        set()):
                message = await _handler.handle(event=event)
                if message:
                    await self.messages_queue.put(message)

    async def process_outbox_message(self, event: NewMessageLongPollEvent):
        raise NotImplementedError

    async def listener(self):
        while True:
            response = await self.long_poll.wait()
            updates = response.get('updates', [])
            for update in updates:
                event = long_poll_event_factory(*update)
                await self.handle_long_poll_event(event)

    async def messenger(self):
        print('start messaging')
        while True:
            print('check queue')
            print(self.messages_queue.qsize())
            if not self.messages_queue.empty():
                message = await self.messages_queue.get()
                await self.process_message(message)
            await asyncio.sleep(1)
