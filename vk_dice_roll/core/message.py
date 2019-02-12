from dataclasses import dataclass


@dataclass()
class BaseMessage:
    recipient_id: int


@dataclass()
class TextMessage(BaseMessage):
    content: str


@dataclass()
class StickerMessage(BaseMessage):
    sticker_id: int
