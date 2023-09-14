import random
from typing import Dict, Any

from aiogram import types
from sqlalchemy.orm import sessionmaker

from db import Users
from db.users import get_user_username, get_user, get_top
from func.classes import Battle, TopUser, Huy


async def get_opponent(message: types.Message, session_maker: sessionmaker):

    if message.from_user.id == message.chat.id:
        if message.reply_to_message is not None:
            user_id = message.reply_to_message.from_user.id
            user = await get_user(user_id, user_id, session_maker)
            print("1")
            if user is not None:
                return user

        entities = message.entities
        for entity in entities:
            if entity.type == 'mention':
                username = entity.extract_from(message.text)[1:]
                user = await get_user_username(username, message, session_maker)
                print("2")
                if user is not None:
                    return user

            elif entity.type == 'text_mention':
                user_id = entity.user.id
                user = await get_user(user_id, user_id, session_maker)
                print("3")
                if user is not None:
                    return user

        if len(message.text.split()) > 1 and message.text.split()[1].isdigit():
            place = int(message.text.split()[1])

            user1 = await get_top(message, session_maker, place, place - 1)

            a = 0
            if user1[0].user_id == message.from_user.id and len(user1) > 1:
                a = 1
            user = await get_user(user1[a].user_id, user1[a].user_id, session_maker)
            print("4")
            if user is not None:
                return user

    else:

        if message.reply_to_message is not None:
            user_id = message.reply_to_message.from_user.id
            user = await get_user(user_id, message.chat.id, session_maker)
            if user is not None:
                return user

        entities = message.entities
        for entity in entities:
            if entity.type == 'mention':
                username = entity.extract_from(message.text)[1:]
                user = await get_user_username(username, message, session_maker)
                if user is not None:
                    return user

            elif entity.type == 'text_mention':
                user_id = entity.user.id
                user = await get_user(user_id, message.chat.id, session_maker)
                if user is not None:
                    return user

        if len(message.text.split()) > 1 and message.text.split()[1].isdigit():
            place = int(message.text.split()[1])
            user1 = await get_top(message, session_maker, place, place - 1)
            a = 0
            if user1[0].user_id == message.from_user.id and len(user1) > 1:
                a = 1

            user = await get_user(user1[a].user_id, message.chat.id, session_maker)
            print(user)
            if user is not None:
                return user

    return None


async def battle(attacker: Users, defender: Users) -> Battle:

    diff = defender.length - attacker.length

    balancer = 0

    if diff < 70:
        balancer = 0
    elif 70 < diff <= 100:
        balancer = 5
    elif 100 < diff <= 150:
        balancer = 15
    elif 150 < diff <= 200:
        balancer = 20
    elif 200 < diff <= 250:
        balancer = 30
    elif 250 < diff <= 350:
        balancer = 40
    elif diff > 350:
        balancer = 47

    victory = random.randint(-50, 50) + (attacker.force - defender.force) - balancer
    if victory > 5:
        a = random.randint(4, 10)
        batt = Battle(a // 2, -a)
    elif victory < -5:
        a = random.randint(4, 10)
        batt = Battle(-a // 2, a // 2)
    else:
        batt = Battle(0, 0)

    return batt


async def shorter(user, length_str):
    user = TopUser(user.row_number, user.user_id, user.chat_id, user.name, user.chat_name, user.length)

    if user.chat_id == user.user_id:
        user.chat_name = 'ЛС'

    if len(user.name) > length_str//2 and len(user.chat_name) > length_str//2:
        user.name = user.name[:length_str//2 - 1].strip() + '..'
        user.chat_name = user.chat_name[: length_str//2 - 1].strip() + '..'

    elif len(user.name + user.chat_name) > length_str + 1:
        if len(user.name) > length_str//2:
            user.name = user.name[:length_str - 2 - len(user.chat_name)].strip() + '..'

        if len(user.chat_name) > length_str//2:
            user.chat_name = user.chat_name[:length_str - 2 - len(user.name)].strip() + '..'

    return user


async def huy(is_battle):
    bonus = Huy()
    a = random.randint(-10, 20)
    if a < -2 or a > 2:
        bonus.adder = a
    else:
        bonus.adder = 0

    if is_battle is not None:
        return bonus

    if a := random.randint(0, 100) < 15:
        if a < 7:
            bonus.defense = -3
        elif 7 <= a <= 10:
            bonus.defense = 1
        else:
            bonus.defense = -1

    if a := random.randint(0, 100) < 10:
        if a < 7:
            bonus.attack = -3
        else:
            bonus.attack = 1

    if random.randint(0, 100) < 30:
        bonus.force = random.randint(-15, 20)

    if a := random.randint(0, 100) < 4:
        if a < 2:
            bonus.trys = -1
        else:
            bonus.trys = 1

    return bonus
