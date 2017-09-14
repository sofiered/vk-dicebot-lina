import asyncio
from app.bot import Bot2
import settings
import random
import re
import functools


dice_regexp = r'(\d+)[d|д](\d+)\s*([\+|-]\d+)?'


async def func2():
    bot = await Bot2.create(settings.LOGIN, settings.PASSWORD)

    async def handler(message):
        message_text = message['message'].lower()
        parse_result = re.findall(dice_regexp, message_text)

        if message_text.startswith('бот'):
            if 'дайс' in message_text:
                await bot.send_message(
                    recepient_id=message['sender'],
                    message='D20: {}'.format(random.randint(1,20)))
            elif parse_result:
                amount, dice, modif = map(lambda x: int(x) if x else 0,
                                          parse_result[0])
                dice_pool = [random.randint(1, dice) for i in range(amount)]
                await bot.send_answer(
                    message,
                    '({}){} = {}'.format(
                        ' + '.join(map(str, dice_pool)),
                        (str(modif) if modif < 0 else '+{}'.format(modif)) if modif else '',
                        functools.reduce(lambda x, y: x + y, dice_pool) + modif))

    async def conf_handler(message):
        message_text = message['message'].lower()
        if message_text.startswith('бот'):
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

    bot.add_handler(handler=handler)
    bot.add_handler(handler=conf_handler,message_type=bot.STATUSES['CONF'])

    await bot.start()

loop = asyncio.get_event_loop()
loop.run_until_complete(func2())