from vk_dice_roll.core.bot import VkBot
from vk_dice_roll.core.event import EventType, NewMessageLongPollEvent
from .handlers import LinaInboxMessageHandler


class Lina(VkBot):
    handler_classes = {EventType.NewMessage: LinaInboxMessageHandler}

    def __init__(self, admin_id: str, secret_key: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.admin_id = admin_id
        self.secret_key = secret_key
        self.is_cheating: bool = False

    async def process_outbox_message(self, event: NewMessageLongPollEvent):
        pass

    async def send_error_sticker(self, peer_id: int):
        await self.send_sticker(peer_id=peer_id,
                                sticker_id=8471)
