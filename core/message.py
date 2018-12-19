from dataclasses import dataclass
from typing import TypeVar

@dataclass()
class BaseMessage:
    pass

Message = TypeVar('Message', bound=BaseMessage)

@dataclass()
class TextMessage(BaseMessage):
    recipient_id: int
    content: str


@dataclass()
class StickerMessage(BaseMessage):
    recipient_id: int
    content: int
