from core.bot import VkBot
from core.event import EventType, T

class Lina(VkBot):
    def __init__(self, admin_id: str, secret_key: str,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.admin_id = admin_id
        self.secret_key = secret_key

    async def handle_long_poll_event(self, event_type: EventType, event: T):
        print(event_type, event)
