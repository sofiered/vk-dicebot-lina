import functools
import random
import re
from itertools import chain
from typing import Any, List, Type, Optional, Union, Tuple

from vk_dice_roll.core.event import NewMessageLongPollEvent, MessageFlags
from vk_dice_roll.core.handlers import InboxMessageHandler
from vk_dice_roll.core.message import TextMessage, StickerMessage, Message


class LinaInboxMessageHandler(InboxMessageHandler):
    trigger_word: Optional[Union[Tuple, str]] = None
    message_type: Type = Type[Message]
    required_flags: Optional[set] = None

    def trigger(self, event: NewMessageLongPollEvent) -> bool:
        return self._check_flags(event.flags) \
               and self._check_trigger(event.text)

    def _check_trigger(self, text: str) -> bool:
        return self.trigger_word is not None and self.trigger_word in text

    def _check_flags(self, flags: set):
        return self.required_flags is None or self.required_flags <= flags

    async def get_type_class(self):
        return self.message_type

    async def _handle(
            self,
            type_class: Type[Message],
            event: NewMessageLongPollEvent) -> Message:
        self.bot.log.info('handling event: %s' % event)
        content = await self.get_content(event)
        args = [event.peer_id] + (content or [])
        self.bot.log.info('making message %s with args %s' % (type_class,
                                                              args))

        return type_class(*args)

    async def get_content(self, event: NewMessageLongPollEvent) -> List[Any]:
        raise NotImplementedError


class Dice20MessageHandler(LinaInboxMessageHandler):
    trigger_word = 'дайс'
    message_type = TextMessage

    async def get_content(
            self,
            event: NewMessageLongPollEvent) -> List[Any]:
        result = 'дайс D20: %s' % (
            20 if self.bot.is_cheating and 'ч' in event.text
            else random.SystemRandom().randint(1, 20))
        return [result]


class MeowMessageHandler(LinaInboxMessageHandler):
    trigger_word = 'мяу'
    message_type = StickerMessage

    async def get_content(self,
                          event: NewMessageLongPollEvent) -> List[Any]:
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
        return [random.choice(cats_id)]


class DiceRegexpMessageHandler(LinaInboxMessageHandler):
    message_type = TextMessage
    trigger_word = re.compile(r'(\d+)[dдк](\d+)\s*([+-]\d+)?')

    def trigger(self, event: NewMessageLongPollEvent):
        return bool(self.trigger_word.match(event.text))

    async def get_content(self,
                          event: NewMessageLongPollEvent) -> List[Any]:
        parse_result = self.trigger_word.findall(event.text)
        amount, dice, modifier = map(lambda x: int(x) if x else 0,
                                     parse_result[0])
        if amount + dice > 1000:
            return ['Слишком много! Я не справлюсь!']
        if amount < 1:
            return ['Я так не умею']
        if dice < 1:
            return ['У меня нет с собой %s-стороннего дайса' % dice]
        dice_pool = [random.SystemRandom().randint(1, dice)
                     if not (self.bot.is_cheating and 'ч' in event.text)
                     else dice for _ in range(amount)]
        result = '(%s)%s = %s' % (' + '.join(map(str, dice_pool)),
                                  (modifier if modifier < 0
                                   else '+%s' % modifier) if modifier else '',
                                  functools.reduce(lambda x, y: x + y,
                                                   dice_pool) + modifier)
        return [result]


class CheatSwitcherMessageHandler(LinaInboxMessageHandler):
    message_type = TextMessage

    def trigger(self, event: NewMessageLongPollEvent) -> bool:
        return self.bot.secret_key in event.text \
               and self.bot.admin_id == event.sender

    async def _handle(self, type_class: Type[Message],
                      event: NewMessageLongPollEvent) -> Message:
        self.bot.is_cheating = not self.bot.is_cheating
        print('читер', type_class)
        return await super()._handle(type_class, event)

    async def get_content(self,
                          event: NewMessageLongPollEvent) -> List[Any]:
        return [str(self.bot.is_cheating)]


class WhereArePostsMessageHandler(LinaInboxMessageHandler):
    message_type = TextMessage
    trigger_word = 'посты'
    posts_answers = [
        'Сегодня будет, но позже',
        'Я уже пишу',
        'Вечером',
        'Я хз, что писать',
        'Вдохновения нет((('
    ]

    async def get_content(self,
                          event: NewMessageLongPollEvent) -> List[Any]:
        return [random.choice(self.posts_answers)]


class GetAdviceMessageHandler(LinaInboxMessageHandler):
    trigger_word = ('что делать', 'как быть', 'посоветуй', 'дай совет')
    advices = [
        'Если ты проявишь инициативу, успех не заставит себя ждать',
        'Твои надежды и планы сбудутся сверх всяких ожиданий',
        'Кто-то старается помешать или навредить тебе',
        'Будь осторожен: тебя хотят обмануть!',
        'Ты надеешься не напрасно!',
        'Проблема внутри тебя',
        'Сядь и осмотрись',
        'Ты идешь не туда, надо было поворачивать налево!',
        'Это ещё не все что с тобой сегодня случится',
        'Хватит крутиться вокруг мира',
        'Пора попросить помощи у друга',
        'Нужно запастись ресурсами и построить Зиккурат',
        'Время постоять в сторонке и обдумать',
        'Мыслишь верно, но не так',
        'Время странствий пришло к концу, ты на месте. Ура! Ура!',
        'Не грусти, найдешь ещё веселье',
        'Не стой, беги!',
        'Ты надеешься не напрасно!',
        'Ты устал, отдохни чуток',
        'Ничего советовать не буду, ты и так знаешь что делать'
    ]

    def trigger(self, event: NewMessageLongPollEvent):
        return any(keyword in event.text for keyword in self.trigger_word)

    async def get_content(self,
                          event: NewMessageLongPollEvent):
        return [random.choice(self.advices)]


class SayHelloMessageHandler(LinaInboxMessageHandler):
    message_type = TextMessage
    trigger_word = 'привет'

    def trigger(self, event: NewMessageLongPollEvent):
        return (self.trigger_word in event.text
                and event.sender == self.bot.admin_id)

    async def get_content(self,
                          event: NewMessageLongPollEvent) -> List[Any]:
        hellos = ['Привет',
                  'Здравствуйте',
                  'Хай!',
                  'Йоу!'
                  ]
        return ['Привет, мастер!' if event.sender == self.bot.admin_id
                else random.choice(hellos)]


class LoveYouMessageHandler(LinaInboxMessageHandler):
    message_type = TextMessage
    trigger_word = ('люблю тебя', 'я тебя люблю')

    def trigger(self, event: NewMessageLongPollEvent):
        return any(keyword in event.text for keyword in self.trigger_word)

    async def get_content(self,
                          event: NewMessageLongPollEvent):
        if event.sender == self.bot.admin_id:
            return ['Я тоже тебя люблю <3']
        else:
            return ['А я тебя нет']


class InfoMessageHandler(LinaInboxMessageHandler):
    message_type = TextMessage
    trigger_word = 'инфа'

    async def get_content(
            self,
            event: NewMessageLongPollEvent):
        info = random.SystemRandom().randint(1, 101)
        if info == 100:
            return ['инфа сотка']
        elif info == 101:
            return ['инфа 146%']
        else:
            return ['инфа %s%%' % info]


class IntervalRandomMessageHandler(LinaInboxMessageHandler):
    message_type = TextMessage
    interval_regexp = r'от\s*(\d+)\s*до\s*(\d+)?'
    trigger_word = 'рандом'

    async def get_content(
            self,
            event: NewMessageLongPollEvent) -> List[Any]:
        parse_result = re.findall(self.interval_regexp, event.text)
        _min, _max = map(lambda x: int(x), parse_result[0])
        if _min > _max:
            _min, _max = _max, _min
        result = random.SystemRandom().randint(_min, _max)
        return ['от %s до %s результат: %s ' % (_min, _max, result)]


class WhoIsChosenMessageHandler(LinaInboxMessageHandler):
    trigger_word = 'кто избран'
    message_type = TextMessage
    required_flags = {MessageFlags.Conference}

    async def get_content(self, event: NewMessageLongPollEvent):
        users = await self.bot.get_chat_users(event.peer_id)
        return ['%s, ты избран!' % random.choice(users)]


class WhoIsGuiltyMessageHandler(LinaInboxMessageHandler):
    trigger_word = 'кто виноват'
    message_type = TextMessage
    guilty = [
        'Да это все массонский заговор',
        'Путин, кто же еще',
        'Это происки сатаны',
        'Рептилоиды, они же управляют всей планетой',
        'Судьба...',
        'Не знаю, но точно не я!',
        'Это все я, прости',
        'Глобальное потепление',
        'Ты сам. А кто же еще?',
        'Телевизор',
        'Интернет',
        'Тупые школьники'
    ]

    async def get_content(self, event: NewMessageLongPollEvent):
        if (random.randint(1, 10) == 6
                and MessageFlags.Conference in event.flags):
            users = await self.bot.get_chat_users(event.peer_id)
            return ['Это %s во всем виноват!' % random.choice(users)]
        else:
            return [random.choice(self.guilty)]
