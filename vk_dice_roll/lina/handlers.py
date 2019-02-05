import random

from itertools import chain
from typing import Optional, Union

from vk_dice_roll.core.event import NewMessageLongPollEvent
from vk_dice_roll.core.handlers import InboxMessageHandler
from vk_dice_roll.core.message import TextMessage, StickerMessage, Message


class LinaInboxMessageHandler(InboxMessageHandler):
    trigger_word: Optional[str] = None
    message_type = TextMessage

    def trigger(self, _event: NewMessageLongPollEvent) -> bool:
        print('check trigger', self.trigger_word)
        result =  self.trigger_word is not None \
               and self.trigger_word.lower() in _event.text
        print(result)
        return result

    async def _handle(self,
                      event: NewMessageLongPollEvent) -> Optional[Message]:
        content = await self.get_content(event)
        if content is None:
            return
        return self.message_type(recipient_id=event.peer_id, content=content)

    async def get_content(self,
                          event: NewMessageLongPollEvent) -> Optional[str]:
        raise NotImplementedError



class LinaDiceMessageHandler(LinaInboxMessageHandler):
    trigger_word = 'дайс'

    async def get_content(
            self,
            event: NewMessageLongPollEvent) -> Optional[Union[str, int]]:
        result = 'дайс D20: {}'.format(random.SystemRandom().randint(1, 20))
        return result


class LinaMeowMessageHandler(LinaInboxMessageHandler):
    trigger_word = 'мяу'
    message_type = StickerMessage

    async def get_content(self,
                          event: NewMessageLongPollEvent) -> Optional[int]:

        peachy_ids = range(49, 97)
        rumka_ids = range(5582, 5630)
        misti_ids = range(5701, 5745)
        seth_ids = range(6109, 6156)
        lovely_ids = range(7096, 7143)

        cats_id = [cat for cat in chain(peachy_ids,
                                        rumka_ids,
                                        misti_ids,
                                        seth_ids,
                                        lovely_ids)]
        return random.choice(cats_id)
