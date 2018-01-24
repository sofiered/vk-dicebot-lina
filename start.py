import asyncio
from app.bot import Bot2
import random
import re
import functools
import os
from itertools import chain

dice_regexp = r'(\d+)[d|д](\d+)\s*([\+|-]\d+)?'

bot_names = ('бот', 'лина', 'народ')

peachy_ids = range(49,97)
rumka_ids = range(5582, 5630)
misti_ids = range(5701, 5745)

cats_id = [cat for cat in chain(peachy_ids, rumka_ids, misti_ids)]


def message_to_bot(func):
    async def decorated_func(message):
        text = message['message'].lower()
        if text.startswith(bot_names):
            await func(message, text)
    return decorated_func


async def main():
    if 'HEROKU_APP' in os.environ:
        login = os.environ.get('LOGIN', '')
        password = os.environ.get('PASSWORD', '')
        secret_key = os.environ.get('SECRET_KEY')
    else:
        import local_settings
        login = local_settings.LOGIN
        password = local_settings.PASSWORD
        secret_key = local_settings.SECRET_KEY

    bot = await Bot2.create(login, password)

    @message_to_bot
    async def cheat_switcher(message, text):
        if secret_key in text:
            bot.cheat_switch()
            await bot.send_answer(message=message,
                                  answer=str(bot.is_cheating))

    @message_to_bot
    async def dice_roller(message, text):
        parse_result = re.findall(dice_regexp, text)
        cheat = bool('ч' in text and bot.is_cheating)
        if 'дайс' in text:
            await bot.send_message(
                recepient_id=message['sender'],
                message='D20: {}'.format(
                    random.SystemRandom().randint(1, 20) if not cheat else 20))
        elif parse_result:
            amount, dice, modifier = map(lambda x: int(x) if x else 0,
                                      parse_result[0])
            dice_pool = [random.SystemRandom().randint(1, dice)
                         if not cheat else dice for _ in range(amount)]
            await bot.send_answer(
                message,
                '({}){} = {}'.format(
                    ' + '.join(map(str, dice_pool)),
                    (str(modifier) if modifier < 0 else '+{}'.format(modifier))
                    if modifier else '',
                    functools.reduce(lambda x, y: x + y,
                                     dice_pool) + modifier))

    @message_to_bot
    async def who_is_chosen(message, text):
        if 'кто избран' in text:
            chosen_one = (
                random.choice(
                    list(
                        filter(
                            lambda x: x.get('id') != bot.get_account_id(),
                            await bot.get_chat_users(message['sender'])
                        )
                    )
                )
            )
            await bot.send_answer(message=message,
                                  answer='{} {}, ты избран!'.format(
                                      chosen_one.get('first_name'),
                                      chosen_one.get('last_name')
                                  ))

    @message_to_bot
    async def where_is_posts(message, text):
        posts_answers = [
            'Сегодня будет, но позже',
            'Я уже пишу',
            'Вечером',
            'Я хз, что писать',
            'Вдохновения нет((('
        ]
        if 'посты' in text:
            await bot.send_answer(message=message,
                                  answer=random.choice(posts_answers))

    @message_to_bot
    async def send_cat(message, text):
        if 'мяу' in text:
            await bot.send_sticker(send_to=message['sender'],
                                   sticker_id=random.choice(cats_id))

    @message_to_bot
    async def get_advice(message, text):
        want_advice = ('что делать', 'как быть', 'посоветуй', 'дай совет')
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
            'Хватит крутится вокруг мира',
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
        if any(keyword in text for keyword in want_advice):
            await bot.send_answer(message=message,
                                  answer=random.choice(advices))

    bot.add_handler(handler=dice_roller)
    bot.add_handler(handler=cheat_switcher)
    bot.add_handler(handler=where_is_posts)
    bot.add_handler(handler=send_cat)
    bot.add_handler(handler=get_advice)
    bot.add_handler(handler=who_is_chosen, message_type=bot.STATUSES['CONF'])

    await bot.start()

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
