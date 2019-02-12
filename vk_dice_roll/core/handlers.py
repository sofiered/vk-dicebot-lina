from typing import Optional, Union

from .event import NewMessageLongPollEvent
from .message import TextMessage, StickerMessage


class InboxMessageHandler:
    def trigger(self, _event: NewMessageLongPollEvent) -> bool:
        raise NotImplementedError

    async def handle(
            self,
            event: NewMessageLongPollEvent) -> Optional[Union[TextMessage,
                                                              StickerMessage]]:
        if self.trigger(event):
            return await self._handle(event)
        else:
            return None

    async def _handle(
            self,
            event: NewMessageLongPollEvent) -> Optional[Union[TextMessage,
                                                              StickerMessage]]:
        raise NotImplementedError
