from enum import Enum
from logging import getLogger
from typing import Union


class EventType(Enum):
    UpdateMessageFlags = 1
    SetMessageFlags = 2
    DropMessageFlags = 3
    NewMessage = 4
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
    Outbox = 2
    Replied = 4
    Important = 8
    Chat = 16
    Friends = 32
    Spam = 64
    Deleted = 128
    Fixed = 256
    Media = 512
    Conference = 8192
    Hidden = 65536


logger = getLogger('lina').getChild('history')


class DefaultLongPollEvent:
    pass


class NewMessageLongPollEvent(DefaultLongPollEvent):
    def __init__(self, *data) -> None:
        logger.info('recieving data: %s' % [data])
        self.message_id: int = data[1]
        self.flags_raw: int = data[2]
        self.flags: set = {flag for flag in MessageFlags
                           if flag.value & self.flags_raw}
        self.peer_id: int = data[3]
        self.text: str = data[5].lower()
        self.sender: int = int(data[6].get('from', self.peer_id))

    def __repr__(self):
        return 'sender: %s, flags: %s, text: %s' % (self.sender,
                                                    self.flags,
                                                    self.text)


def long_poll_event_factory(*data) -> Union[DefaultLongPollEvent,
                                            NewMessageLongPollEvent]:
    if data[0] == EventType.NewMessage.value:
        return NewMessageLongPollEvent(*data)
    else:
        return DefaultLongPollEvent()
