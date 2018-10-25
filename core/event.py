from enum import Enum
from typing import Type, TypeVar, List, Tuple, Any

class EventType(Enum):
    UpdateMessageFlags = 1
    SetMessageFlags = 2
    DropMessageFlags = 3
    AddMessage = 4
    EditMessage = 5
    ReadIncomingMessage = 6
    ReadOutcomingMessage = 7
    FriendOnline = 8
    FriendOffline = 9
    DropDialogFlags = 10
    UpdateDialogFlags = 11
    SetDialogFlags = 12
    DropAllMessages = 13
    RestoreMessages = 14
    UpdateConferenceParams = 51
    UpdateConferenceInfo = 52
    UserTypesInDialog = 61
    UserTypesInConference = 62
    UserCalling = 70
    DropLeftMenuCounter = 80
    UpdateNotifySettings = 114

class Flags(Enum):
    UNREAD = 1
    OUTBOX =  2
    REPLIED = 4
    IMPORTANT = 8
    CHAT = 16
    FRIENDS = 32
    SPAM = 64
    DELETED = 128
    FIXED = 256
    MEDIA = 512
    CONF = 8192
    HIDDEN = 65536


class DefaultLongPollEvent:
    pass

T = TypeVar('T', bound=DefaultLongPollEvent)


class NewMessageLongPollEvent(DefaultLongPollEvent):
    def __init__(self, *data) -> None:
        self.message_id: int = data[1]
        self.flags:int = data[2]
        self.outbox:int = self.flags & Flags.OUTBOX.value
        self.peer_id:int = data[3]
        self.text: str = data[5].lower()
        self.sender = data[6].get('from', self.peer_id)


def long_poll_event_factory(*data) -> T:
    if data[0] == EventType.AddMessage.value:
        return NewMessageLongPollEvent(*data)
    else:
        return DefaultLongPollEvent()

