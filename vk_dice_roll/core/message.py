from abc import ABC
from dataclasses import dataclass
from typing import TypeVar


@dataclass()
class BaseMessage(ABC):
    recipient_id: int


@dataclass()
class TextMessage(BaseMessage):
    content: str


@dataclass()
class StickerMessage(BaseMessage):
    sticker_id: int


Message = TypeVar('Message', bound=BaseMessage)
