from app.handlers import LinaAddMessageHandler
from core.event import EventType


from core.vkbot import VkBot

class LinaBot(VkBot):
    _default_names = ('лина', 'бот', 'народ')

    _handler_types = {
        EventType.AddMessage: LinaAddMessageHandler
    }

    dice_regexp = r'(\d+)[d|д|к](\d+)\s*([\+|-]\d+)?'
    interval_regexp = r'от\s*(\d+)\s*до\s*(\d+)?'

    # stickers
    peachy_ids = range(49, 97)
    rumka_ids = range(5582, 5630)
    misti_ids = range(5701, 5745)
    seth_ids = range(6109, 6156)
    lovely_ids = range(7096, 7143)



    def __init__(self, admin_id:int, secret_key:str, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.admin_id: int = admin_id
        self.secret_key = secret_key
