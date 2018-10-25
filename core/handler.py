from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from .vkbot import VkBot
    from .event import T, NewMessageLongPollEvent

class BaseHandler:
    @staticmethod
    async def handle(bot:'VkBot', event:'T'):
        raise NotImplementedError

class AddMessageHandler(BaseHandler):
    @classmethod
    async def handle(cls, bot: 'VkBot', event:'NewMessageLongPollEvent'):
        print(' message handler')
        if event.text.startswith(bot.names):
            await cls._handle(bot, event)

    @classmethod
    async def _handle(cls, bot:'VkBot', event:'NewMessageLongPollEvent'):
        raise NotImplementedError

def incoming(func):
    async def decorated_func(cls, bot: 'VkBot', event:'NewMessageLongPollEvent'):
        if not event.outbox:
            await func(cls, bot, event)

    return decorated_func