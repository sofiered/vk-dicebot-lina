import asyncio
from app.bot import Bot2
import random
import re
import functools
import os
from itertools import chain

loop = asyncio.get_event_loop()

dice_regexp = r'(\d+)[d|д|к](\d+)\s*([\+|-]\d+)?'
interval_regexp = r'от\s*(\d+)\s*до\s*(\d+)?'

bot_names = ('бот', 'лина', 'народ')

peachy_ids = range(49,97)
rumka_ids = range(5582, 5630)
misti_ids = range(5701, 5745)
seth_ids = range(6109,6156)
lovely_ids = range(7096,7143)

cats_id = [cat for cat in chain(peachy_ids,
                                rumka_ids,
                                misti_ids,
                                seth_ids,
                                lovely_ids)]


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
        admin_key = int(os.environ.get('ADMIN_KEY'))
    else:
        import local_settings
        login = local_settings.LOGIN
        password = local_settings.PASSWORD
        secret_key = local_settings.SECRET_KEY
        admin_key = local_settings.ADMIN_KEY

    bot = await Bot2.create(login, password, loop)

    def admin_only(func):
        async def decorated_func(message):
            if message['speaker'] == admin_key:
                await func(message)

        return decorated_func

    @message_to_bot
    async def cheat_switcher(message, text):
        if secret_key in text:
            bot.cheat_switch()
            await bot.send_message(message=message,
                                   answer=str(bot.is_cheating))

    @message_to_bot
    async def dice_roller(message, text):
        parse_result = re.findall(dice_regexp, text)
        cheat = bool('ч' in text and bot.is_cheating)
        if 'дайс' in text:
            await bot.send_message(answer_to=message,
                                   text='D20: {}'.format(
                    random.SystemRandom().randint(1, 20) if not cheat else 20))
        elif parse_result:
            amount, dice, modifier = map(lambda x: int(x) if x else 0,
                                      parse_result[0])
            print("{} {} {}".format(amount, dice, modifier))
            if amount > 1000 or dice > 1000:
                await bot.send_message(message, "Ты наркоман? Зачем тебе столько?")
                return
            if amount < 1:
                await bot.send_message(message, 'Зачем бросать дайс менее одного раза?')
                return
            if dice < 1:
                await bot.send_message(message, "Я не умею бросить {}-сторонний дайс".format(dice))
                return
            dice_pool = [random.SystemRandom().randint(1, dice)
                         if not cheat else dice for _ in range(amount)]
            await bot.send_message(
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
            await bot.send_message(answer_to=message,
                                   text='{} {}, ты избран!'.format(
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
            await bot.send_message(answer_to=message,
                                   text=random.choice(posts_answers))

    @message_to_bot
    async def send_cat(message, text):
        if 'мяу' in text:
            await bot.send_sticker(answer_to=message,
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
        if any(keyword in text for keyword in want_advice):
            await bot.send_message(message=message,
                                   answer=random.choice(advices))

    @message_to_bot
    async def who_is_guily(message, text):
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
        if 'кто виноват' in text:
            if random.choice(range(10)) == 6 and message['sender'] > 2000000000:
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
                await bot.send_message(message=message,
                                       answer='Это {} {} во всем виноват'.format(
                                          chosen_one.get('first_name'),
                                          chosen_one.get('last_name')))
            else:
                await bot.send_message(message=message,
                                       answer=random.choice(guilty))

    @admin_only
    @message_to_bot
    async def sey_hello_to_master(message, text):
        if 'привет' in text:
            await bot.send_message(message=message, answer='Привет, создатель')

    @message_to_bot
    async def info(message, text):
        if 'инфа' in text:
            infa = random.SystemRandom().randint(1,101)
            if infa == 100:
                answer = 'инфа сотка'
            elif infa == 101:
                answer = 'инфа 146%'
            else:
                answer = 'инфа %s%%' % infa
            await bot.send_message(message=message, answer=answer)

    @message_to_bot
    async def love_you(message, text):
        love = ('люблю тебя', 'я тебя люблю')
        if any(keyword in text for keyword in love):
            if message['speaker'] == admin_key:
                await bot.send_message(message, "Я тоже тебя люблю <3")
            else:
                await bot.send_message(message, "А я тебя нет")

    @message_to_bot
    async def get_help(message, text):
        need_help = ('команды', 'помощь')
        answer = 'Отзываюсь на Лина, Бот и Народ в начале сообщения. Регистр не важен. \r\n' \
                 'Кроме команды в сообщение можно добавлять любой текст. ' \
                 'Можно использовать несколько команд в одном сообщении, ' \
                 'они выполнятся в случайном порядке\r\n' \
                 '-- броски кубиков --\r\n' \
                 'команды в формате 2д4, 1d12 или 3к6. Можно прибавлять и вычитать модификаторы, например, 1д12 +3\r\n' \
                 'команда "дайс" это то же самое, что и 1d20 \r\n' \
                 '-- другие команды --\r\n' \
                 '"рандом от X до Y" возвращает случайное число в заданных границах \r\n' \
                 '"кто избран" указывает на случайного человека в беседе. Не работает в личных сообщениях\r\n' \
                 '"кто виноват" поможет найти причину всех бед\r\n' \
                 '"посты" объясняет, почему никто ничего не пишет\r\n' \
                 '"инфа" определит степень достоверности факта\r\n' \
                 '"мяу" покажет случайный стикер с котиком'
        if any(keyword in text for keyword in need_help):
            await bot.send_message(message=message,
                                   answer=answer)

    @message_to_bot
    async def interval_random(message, text):
        if 'рандом' in text:
            parse_result = re.findall(interval_regexp, text)
            if parse_result:
                min, max = map(lambda x: int(x), parse_result[0])
                if min > max:
                    min, max = max, min
                value = random.SystemRandom().randint(min, max)
                await bot.send_message(message, "(от {} до {})={}".format(min,
                                                                          max,
                                                                          value))


    bot.add_handler(handler=dice_roller)
    bot.add_handler(handler=cheat_switcher)
    bot.add_handler(handler=where_is_posts)
    bot.add_handler(handler=send_cat)
    bot.add_handler(handler=get_advice)
    bot.add_handler(handler=who_is_guily)
    bot.add_handler(handler=sey_hello_to_master)
    bot.add_handler(handler=info)
    bot.add_handler(handler=get_help)
    bot.add_handler(handler=love_you)
    bot.add_handler(handler=interval_random)
    bot.add_handler(handler=who_is_chosen, message_type=bot.STATUSES['CONF'])

    await bot.start()


loop.run_until_complete(main())
