import asyncio
from app.bot import Bot2
import random
import re
import functools
import os

dice_regexp = r'(\d+)[d|д](\d+)\s*([\+|-]\d+)?'

bot_names = ('бот', 'лина', 'народ')


async def func2():
    login = os.environ.get('LOGIN', '')
    password = os.environ.get('PASSWORD', '')
    secret_key = os.environ.get('SECRET_KEY')

    bot = await Bot2.create(login, password)

    async def cheat_switcher(message):
        message_text = message['message'].lower()
        if message_text.startswith(bot_names):
            if secret_key in message_text:
                bot.cheat_switch()
                await bot.send_answer(message=message,
                                      answer=str(bot.is_cheating))

    async def dice_roller(message):
        message_text = message['message'].lower()
        parse_result = re.findall(dice_regexp, message_text)

        if message_text.startswith(bot_names):
            cheat = bool('ч' in message_text and bot.is_cheating)
            if 'дайс' in message_text:
                await bot.send_message(
                    recepient_id=message['sender'],
                    message='D20: {}'.format(
                        random.SystemRandom().randint(1,20))
                    if not cheat else 20)
            elif parse_result:
                amount, dice, modif = map(lambda x: int(x) if x else 0,
                                          parse_result[0])
                dice_pool = [random.SystemRandom().randint(1, dice)
                             if not cheat else dice for i in range(amount)]
                await bot.send_answer(
                    message,
                    '({}){} = {}'.format(
                        ' + '.join(map(str, dice_pool)),
                        (str(modif) if modif < 0 else '+{}'.format(modif)) if modif else '',
                        functools.reduce(lambda x, y: x + y, dice_pool) + modif))

    async def who_is_chosen(message):
        message_text = message['message'].lower()
        if message_text.startswith(bot_names):
            if 'кто избран' in message_text:
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

    async def where_is_posts(message):
        posts_answers = [
            'Сегодня будет, но позже',
            'Я уже пишу',
            'Вечером',
            'Я хз, что писать',
            'Вдохновения нет((('
        ]
        message_text = message['message'].lower()
        if message_text.startswith(bot_names):
            if 'посты' in message_text:
                await bot.send_answer(message=message,
                                      answer=random.choice(posts_answers))

    async def send_peachy(message):
        peachy_ids = [66, 89, 63, 75, 71, 86, 50, 68, 58, 65, 59, 83, 70, 77,
                      88, 87, 49, 54, 56, 67, 73, 51, 55, 57, 72, 61, 60, 64,
                      81, 84, 79, 96, 74, 78, 52, 80, 62, 82, 53, 69, 94, 90,
                      91, 85, 92, 93, 95, 76]
        message_text = message['message'].lower()
        if message_text.startswith(bot_names):
            if 'мяу' in message_text:
                await bot.send_sticker(send_to=message['sender'],
                                       sticker_id=random.choice(peachy_ids))

    bot.add_handler(handler=dice_roller)
    bot.add_handler(handler=cheat_switcher)
    bot.add_handler(handler=where_is_posts)
    bot.add_handler(handler=send_peachy)
    bot.add_handler(handler=who_is_chosen,message_type=bot.STATUSES['CONF'])

    await bot.start()

loop = asyncio.get_event_loop()
loop.run_until_complete(func2())