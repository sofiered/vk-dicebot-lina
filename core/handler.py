from .event import MessageFlags
from typing import TYPE_CHECKING, Set


if TYPE_CHECKING:
    from .vkbot import VkBot
    from .event import T, NewMessageLongPollEvent


class EmptyTriggerError(Exception): ...


class BaseHandler:
    def __init__(self, bot: 'VkBot'):
        self.bot: VkBot = bot

    async def handle(self, event:'T'):
        raise NotImplementedError


class AddMessageHandler(BaseHandler):
    required_flags:set = set()
    forbidden_flags = {MessageFlags.Outbox}
    trigger:set or str = ''

    async def handle(self,
                     event:'NewMessageLongPollEvent'):
        print(' message handler')
        if self.trigger == '' or self.trigger == set():
            raise EmptyTriggerError()

        if type(self.trigger) == str:
            self.trigger = {self.trigger}

        if not (self.required_flags <= event.flags) \
                or not (self.forbidden_flags & event.flags == set()):
            print('bad flags')
            return

        if not event.text.startswith(self.bot.names):
            print('without name')
            return

        if not any(trigger in event.text for trigger in self.trigger):
            print('without trigger')
            return

        await self._handle(event)

    async def _handle(self,
                      event:'NewMessageLongPollEvent'):
        raise NotImplementedError
