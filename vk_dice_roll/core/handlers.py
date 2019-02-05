from typing import Optional

from .event import NewMessageLongPollEvent
from .message import Message, TextMessage


class InboxMessageHandler():
    def trigger(self, _event: NewMessageLongPollEvent) -> bool:
        raise NotImplementedError

    async def handle(self, event: NewMessageLongPollEvent) -> Optional[Message]:
        if self.trigger(event):
            return await self._handle(event)

    async def _handle(self,
                      event: NewMessageLongPollEvent) -> Optional[Message]:
        raise NotImplementedError
