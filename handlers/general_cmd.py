import asyncio
import random
from typing import Dict, Any

from aiogram import types, Router, F
from aiogram.filters import Command, StateFilter, ChatMemberUpdatedFilter, IS_MEMBER, IS_NOT_MEMBER
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.orm import sessionmaker

from db.users import get_top, get_user_place, get_user, Users, update_user, get_global_top, get_user_global_place, \
    get_count_top, get_count_global_top, semi_refresh_user, get_chats
from func.fsm import BattleState
from func.general_func import get_opponent, battle, shorter, huy
from middlewares.update_data import UpdateData
from aiogram.fsm.context import FSMContext
import texts
from aiogram.exceptions import TelegramRetryAfter

router = Router()

router.message.middleware(UpdateData())
admin_id = '517922464'


@router.message(Command("bot_to_group"), (F.chat.type == "private"))
async def add_chats(message: types.Message):
    text = f'Добавить бота в чат(группу)?\n'
    ib1 = InlineKeyboardButton(text = 'Добавить в чат', url='http://t.me/TestDickBattleBot?startgroup=start_chat')
    builder = InlineKeyboardBuilder()
    builder.add(ib1)
    await message.answer(text, reply_markup=builder.as_markup())


@router.message(Command("help"))
async def helper(message: types.Message):
    await message.answer("Инструкция: https://telegra.ph/Bot-Hueplet-documentationinstruction-09-04")


@router.message(Command("start"))
@router.chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
async def start_chat(event: types.ChatMemberUpdated):
    if isinstance(event, types.Message):
        text = """Привет, я Бот-Хуеплёт!!!
Чтобы начать выращивать член используй /huy

<i>Бот: https://t.me/DickBattleBot
Чат: https://t.me/BotHuepletChat
Канал с новостями: https://t.me/BotHuepletNews</i>
Инструкция: https://telegra.ph/Bot-Hueplet-documentationinstruction-09-04"""
        await event.answer(text)
        await event.delete()

    else:
        if event.from_user.id == event.bot.id:
            text = """Привет, я Бот-Хуеплёт!!!
    
    <i>Бот: https://t.me/DickBattleBot
    Чат: https://t.me/BotHuepletChat
    Канал с новостями: https://t.me/BotHuepletNews</i>"""
            await event.answer(text)


@router.message(Command('top', 'топ'))
async def top_cmd(message: types.Message, session_maker: sessionmaker):
    words = message.text.split()
    count = 0

    if len(words) == 3 and words[1].isdigit() and words[2].isdigit() and int(words[1]) < int(words[2]):
        start = int(words[1]) - 1
        stop = int(words[2])

    elif len(words) == 2 and words[1].isdigit():
        start = 0
        stop = int(words[1])

    else:
        start = 0
        stop = 10

    top_users = await get_top(message, session_maker, stop, start)
    len_top = len(top_users)
    if len_top == 0:
        return 0

    text1 = ''
    if len_top > stop - start:
        len_top -= 1
        if top_users[0].user_id == message.from_user.id:
            user = top_users[0]
            top_users.pop(0)
        else:
            user = top_users[-1]
            top_users.pop()

        if len(user.name) > 20:
            name = user.name[:20] + ".."
        else:
            name = user.name

        text1 += "\n8=======================D\n"
        text1 += f"{user.row_number}|<u>{user.name}</u>: <b>{user.length}</b> см"

    if len_top > 100 and message.chat.id != message.from_user.id:
        len_top = 100

    stop1 = stop
    stop = start + len_top
    whole = len_top//25
    a = 1 if len_top % 25 else 0

    for i in range(whole + a):

        last = start + 25*(i+1) if 25*(i+1) < stop else stop
        cou = await get_count_top(message, session_maker)
        text = f"<b>Топ {start + 1 + 25*i}-{last}/{cou}\n\n</b>"
        part_top = top_users[25*i: last - start]

        for user in part_top:
            if len(user.name) > 20:
                name = user.name[:20]+".."
            else:
                name = user.name

            if user.user_id == message.from_user.id:
                text += f"{user.row_number}|<u>{name}</u>: <b>{user.length}</b> см\n"
            else:
                text += f"{user.row_number}|{name}: <b>{user.length}</b> см\n"

        if i == whole + a - 1:
            text += text1

            await message.answer(text)


@router.message(Command('battle', 'битва'), StateFilter(None))
async def battle_cmd(message: types.Message, session_maker: sessionmaker):
    attacker = await get_user(message.from_user.id, message.chat.id, session_maker)
    attacker: Users
    if attacker.length < 10:
        text = f"<a href ='tg://user?id={attacker.user_id}'>{attacker.name}</a>б, твой член слишком маленький чтобы напасть"
        await message.answer(text)
        return 0

    if attacker.attack == 0:
        text = f"<a href ='tg://user?id={attacker.user_id}'>{attacker.name}</a>, ты не можешь сегодня нападать"
        await message.answer(text)
        return 0

    opponent = await get_opponent(message, session_maker)

    if opponent is None:
        text = f"<a href ='tg://user?id={attacker.user_id}'>{attacker.name}</a>\nНе найдено такого противника"
        return await message.answer(text)
    else:
        opponent = await semi_refresh_user(opponent, session_maker)
    print(opponent.name)
    opponent: Users

    if opponent.user_id == attacker.user_id:
        text = f"<a href ='tg://user?id={attacker.user_id}'>{attacker.name}</a>\nНельзя нападать на себя"
        return await message.answer(text)

    if opponent.length < 10:
        text = f"<a href ='tg://user?id={attacker.user_id}'>{attacker.name}</a>\nНа него нельзя нападать, у него слишком маленький член"
        return await message.answer(text)

    if opponent.defense == 0:
        text = f"<a href ='tg://user?id={attacker.user_id}'>{attacker.name}</a>\nНа него сегодня нельзя нападать"
        return await message.answer(text)

    msg = await message.answer(text=texts.battle[random.randint(0, 16)])

    await asyncio.sleep(1.4)
    result_battle = await battle(attacker, opponent)
    if result_battle.attacker > result_battle.defender:
        text = f"<u><b>Победа!</b></u>\n<a href ='tg://user?id={attacker.user_id}'>{message.from_user.first_name}</a>, ваш член \nувеличился на <b>{result_battle.attacker} см</b>\n\nЧлен <a href ='tg://user?id={opponent.user_id}'>{opponent.name}</a> \nуменьшился на <b>{abs(result_battle.defender)} см</b>"
    elif result_battle.attacker < result_battle.defender:
        text = f"<u><b>Поражение!</b></u>\n<a href ='tg://user?id={attacker.user_id}'>{message.from_user.first_name}</a>, ваш член \nуменьшился на <b>{abs(result_battle.attacker)} см</b>\n\nЧлен <a href ='tg://user?id={opponent.user_id}'>{opponent.name}</a> \nувеличился на <b>{result_battle.defender} см</b>"
    else:
        text = "Ничья"

    opponent.length += result_battle.defender
    opponent.defense -= 1

    attacker.length += result_battle.attacker
    attacker.attack -= 1

    await update_user(opponent, session_maker)
    await update_user(attacker, session_maker)

    if message.chat.id == message.from_user.id:
        text2 = f"На вас напал {attacker.name} @{attacker.username}\n"
        if result_battle.attacker > result_battle.defender:
            text2 += f"<u><b>Поражение!</b></u>\n<a href ='tg://user?id={opponent.user_id}'>{opponent.name}</a>, ваш член \nуменьшился на <b>{abs(result_battle.defender)} см</b>\n\nЧлен <a href ='tg://user?id={attacker.user_id}'>{attacker.name}</a> \nувеличился на <b>{result_battle.attacker} см</b>"
        elif result_battle.attacker < result_battle.defender:
            text2 += f"<u><b>Победа!</b></u>\n<a href ='tg://user?id={opponent.user_id}'>{opponent.name}</a>,, ваш член \nувеличился на <b>{abs(result_battle.defender)} см</b>\n\nЧлен <a href ='tg://user?id={attacker.user_id}'>{attacker.name}</a> \nуменьшился на <b>{result_battle.attacker} см</b>"
        else:
            text2 += "<u><b>Ничья!</b></u>"
        await message.bot.send_message(opponent.chat_id, text2)

    await msg.edit_text(text)
    # await message.answer(text)


@router.callback_query(F.data == "huy")
@router.message(Command('хуй', 'huy'))
async def huy_cmd(message: types.Message, session_maker: sessionmaker, state: FSMContext):
    user = await get_user(message.from_user.id, message.chat.id, session_maker)
    user: Users
    text = f"<a href ='tg://user?id={user.user_id}'>{user.name}</a>\n"
    if user.grows + user.trys <= 0:
        text += "Cегодня больше нельзя\n\n"
        text += f"<i>Длина пэниса: <b>{user.length}</b> см\n"
        # text += f"Место в топе: <b>{(await get_user_place(user.user_id, user.chat_id, session_maker))[3]}</b>\n"
        if user.trys + user.grows > 0:
            text += "Еще одна попытка сегодня</i>"
        elif user.grows + user.trys < 0:
            text += "Следующая попытка послезавтра</i>"
        else:
            text += "Следующая попытка завтра</i>"
        return await message.answer(text)

    is_battle = await state.get_state()
    bonus = await huy(is_battle)

    user.length += bonus.adder
    user.attack += bonus.attack
    user.defense += bonus.defense
    user.trys += bonus.trys
    user.force += bonus.force

    if user.grows > 0:
        user.grows -= 1
    else:
        user.trys -= 1

    await update_user(user, session_maker)

    text += f"<u>Увеличение/уменьшение</u>\n"
    if bonus.adder != 0:
        if bonus.adder > 0:
            text_grows = texts.grows_plus[random.randint(0,9)]
        else:
            text_grows = texts.grows_minus[random.randint(0, 4)]

        text += f"{text_grows} на <b>{abs(bonus.adder)}</b> см\n\n"
    else:
        text_grows = texts.grows_neutral[random.randint(0, 4)]
        text += text_grows + "\n\n"

    if bonus.attack != 0:
        text += "<u>Бафы/дебафы</u>\n"
        if bonus.attack > 0:
            text += f"Водица Байкальская\n"
            text += f"<i>(Сегодня ты можешь напасть на 1 раз больше)</i>"
        elif bonus.attack < 0:
            text += f"Бессилие\n"
            text += f"<i>(Сегодня ты больше не сможешь нападать)</i>"
        text += "\n\n"

    if bonus.defense != 0:
        text += "<u>Бафы/дебафы</u>\n"
        if bonus.defense == 1:
            text += f"Порванные трусы\n"
            text += f"<i>Сегодня на тебя могут напасть на 1 раз больше</i>"
        elif bonus.defense == -3:
            text += f"Православная защита\n"
            text += f"<i>(Сегодня на тебя не смогут напасть)</i>"
        elif bonus.defense == -1:
            text += f"Щит богатыря\n"
            text += f"<i>(Сегодня на тебя могут напасть на 1 раз меньше)</i>"
        text += "\n\n"

    if bonus.force != 0:
        text += "<u>Бафы/дебафы</u>\n"
        text += f"Удача {bonus.force}%\n"
        if bonus.force > 0:
            text += f"<i>(Шанс победить повышен)</i>"
        elif bonus.force < 0:
            text += f"<i>(Шанс победить понижен)</i>"
        text += "\n\n"

    if bonus.trys != 0:
        text += "<u>Бафы/дебафы</u>\n"
        if bonus.trys < 0:
            text += f"День говна\n"
            text += f"<i>(Завтра ты не сможешь вырастить хуй)</i>"
        elif bonus.trys > 0:
            text += f"Дополнительная попытка"
        text += "\n\n"

    text += f"<i>Длина пэниса: <b>{user.length}</b> см\n"
    text += f"Место в топе: <b>{(await get_user_place(user.user_id, user.chat_id, session_maker))[3]}</b>\n"
    if user.trys + user.grows > 0:
        text += "Еще одна попытка сегодня</i>"
    elif user.grows + user.trys < 0:
        text += "Следующая попытка послезавтра</i>"
    else:
        text += "Следующая попытка завтра</i>"

    await message.answer(text)


@router.message(Command('global_top', 'глобальный_топ'))
async def global_top_cmd(message: types.Message, session_maker: sessionmaker):
    words = message.text.split()
    count = 0

    if len(words) == 3 and words[1].isdigit() and words[2].isdigit() and int(words[1]) < int(words[2]):
        start = int(words[1]) - 1
        stop = int(words[2])

    elif len(words) == 2 and words[1].isdigit():
        start = 0
        stop = int(words[1])

    else:
        start = 0
        stop = 10

    top_users = await get_global_top(message, session_maker, stop, start)
    top_users: list
    len_top = len(top_users)

    if len_top == 0:
        return 0

    if message.from_user.id == message.chat.id:
        length_str = 20
    else:
        length_str = 15

    text1 = ''

    if len_top > stop - start:
        len_top -= 1
        if top_users[0].user_id == message.from_user.id and top_users[0].chat_id == message.chat.id:
            user = top_users[0]
            top_users.pop(0)
        else:
            user = top_users[-1]
            top_users.pop()

        user = await shorter(user, length_str)
        text1 += "\n8=========================D\n"
        text1 += f"{user.row_number}|<u>{user.name}[<i>{user.chat_name}</i>]</u>: <b>{user.length}</b>\n"

    if len_top > 100 and message.chat.id != message.from_user.id:
        len_top = 100

    stop1 = stop
    stop = start + len_top
    whole = len_top//25
    a = 1 if len_top % 25 else 0

    cou = await get_count_global_top(session_maker)
    for i in range(whole+a):

        last = start + 25*(i+1) if 25*(i+1) < stop else stop

        text = f"<b>Глобальный топ | {start + 1 + 25*i}-{last}/{cou}</b>\n\n"
        part_top = top_users[25*i: last - start]
        for user in part_top:
            user = await shorter(user, length_str)

            if user.user_id == message.from_user.id and user.chat_id == message.chat.id:
                count += 1
                text += f"{user.row_number}|<u>{user.name}[<i>{user.chat_name}</i>]</u>: <b>{user.length}</b>\n"
            else:
                text += f"{user.row_number}|{user.name}[<i>{user.chat_name}</i>]: <b>{user.length}</b>\n"

        if i == whole + a - 1:
            text += text1

        await message.answer(text)


@router.message(Command('профиль', 'profile'))
async def profile_cmd(message: types.Message, session_maker: sessionmaker, state: FSMContext):
    user = await get_opponent(message, session_maker)

    if user is not None:
        user = await semi_refresh_user(user, session_maker)
    else:
        user = await get_user(message.from_user.id, message.chat.id, session_maker)

    user: Users
    place = await get_user_place(user.user_id, user.chat_id, session_maker)

    place = place.row_number
    text = f"""
<i><u>Профиль</u>:
<b>{user.name}</b>
<b>@{user.username}</b>
Чат: <b>{user.chat_name}</b>
    
Длина пениса: <b>{user.length}</b> см | <b>{user.grows+user.trys}</b> п
Место в топе: <b>{place}</b></i>\n"""
    if await state.get_state() is None:
        text += f"""    
<i>Доп. удача в битве: <b>{user.force}%</b>
Нападениe: <b>{user.attack}/3</b>
Оборона: <b>{user.defense}/3</b></i>
    """
    # builder = InlineKeyboardBuilder()
    # if user.user_id == message.from_user.id and user.grows+user.trys > 0:
    #     builder.add(types.InlineKeyboardButton(text = "Вырастить член", callback_data="huy"))
    await message.answer(text)


@router.message(Command("send_all"))
async def send_all_cmd(message: types.Message, session_maker: sessionmaker):
    if str(message.from_user.id) == admin_id:
        text = message.text.split()[1:]
        text = " ".join(text)
        chats = await get_chats(session_maker)
        for chat in chats:
            try:
                await message.bot.send_message(chat[0], text=text)
            except TelegramRetryAfter:
                print("Слишком много")
                await asyncio.sleep(3)

            except:
                pass
                print("Ошибка")
        await message.answer("Рассылка завершена")

