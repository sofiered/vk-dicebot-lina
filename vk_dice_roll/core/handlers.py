from typing import Optional, Type

from .event import NewMessageLongPollEvent
from .message import Message


class InboxMessageHandler:
    def __init__(self, bot):
        self.bot = bot

    def trigger(self, _event: NewMessageLongPollEvent) -> bool:
        raise NotImplementedError

    async def handle(
            self,
            event: NewMessageLongPollEvent) -> Optional[Message]:
        if self.trigger(event):
            type_class = await self.get_type_class()
            return await self._handle(type_class,
                                      event)
        else:
            return None

    async def get_type_class(self) -> Type[Message]:
        raise NotImplementedError

    async def _handle(
            self,
            type_class: Type[Message],
            event: NewMessageLongPollEvent) -> Message:
        raise NotImplementedError
