import asyncio

import local_settings
from core.vkbot import VkBot
from core.handler import AddMessageHandler, incoming
from core.event import NewMessageLongPollEvent

class EchoHandler(AddMessageHandler):
    @classmethod
    @incoming
    async def _handle(cls, bot: 'VkBot', event: 'NewMessageLongPollEvent'):
        await bot.send_text_message(peer_id=event.peer_id,
                                    text=event.text)

async def main():
    lina = VkBot(app_id=local_settings.APP_ID,
                    login=local_settings.LOGIN,
                    password=local_settings.PASSWORD)
    await lina.start()


if __name__ == '__main__':
    asyncio.run(main())
