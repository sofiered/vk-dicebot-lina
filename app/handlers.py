from core.handler import AddMessageHandler
from core.event import NewMessageLongPollEvent, MessageFlags


class LinaAddMessageHandler(AddMessageHandler):
    async def handle(self,
               event:'NewMessageLongPollEvent'):
        if MessageFlags.Outbox in event.flags:
            return
        await super().handle(event)

    async def _handle(self,
                event:'NewMessageLongPollEvent'):
        await super()._handle(event)

class HelloWorldHandler(LinaAddMessageHandler):
    trigger = 'привет'
    async def _handle(self,
                      event:'NewMessageLongPollEvent'):
        await self.bot.send_text_message(peer_id=event.peer_id,
                                         text='hello world')