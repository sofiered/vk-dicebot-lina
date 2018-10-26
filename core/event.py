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

class MessageFlags(Enum):
    Unread = 1
    Outbox =  2
    Replied = 4
    Important = 8
    Chat = 16
    Friends = 32
    Spam = 64
    Deleted = 128
    Fixed = 256
    Media = 512
    Conference = 8192
    Hidden= 65536


class DefaultLongPollEvent:
    pass

T = TypeVar('T', bound=DefaultLongPollEvent)


class NewMessageLongPollEvent(DefaultLongPollEvent):
    def __init__(self, *data) -> None:
        self.message_id: int = data[1]
        self.flags_raw:int = data[2]
        self.flags = {flag for flag in list(MessageFlags)
                      if flag.value & self.flags_raw}
        self.peer_id:int = data[3]
        self.text: str = data[5].lower()
        self.sender = data[6].get('from', self.peer_id)


def long_poll_event_factory(*data) -> T:
    if data[0] == EventType.AddMessage.value:
        return NewMessageLongPollEvent(*data)
    else:
        return DefaultLongPollEvent()

