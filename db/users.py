import datetime

from aiogram import types
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.functions import count

from .base import BaseModel
from sqlalchemy import Column, Integer, VARCHAR, DATE, select, update, func, desc, or_, and_, BigInteger, delete


class Users(BaseModel):
    __tablename__ = 'users'

    user_id = Column(BigInteger, primary_key=True, nullable=False)
    chat_id = Column(BigInteger, primary_key=True, nullable=False)
    username = Column(VARCHAR(32))
    name = Column(VARCHAR(32))
    chat_name = Column(VARCHAR(32))
    length = Column(Integer, default=0)
    date = Column(DATE, default=datetime.date.today())
    grows = Column(Integer, default=1)
    attack = Column(Integer, default=3)
    defense = Column(Integer, default=3)
    trys = Column(Integer, default=0)
    force = Column(Integer, default=0)

    def __str__(self) -> str:
        return f"<User:{self.user_id}:{self.chat_id}>"


async def get_user(user_id, chat_id, session_maker: sessionmaker):
    async with session_maker() as session:
        async with session.begin():
            result = await session.execute(select(Users).filter(Users.user_id == user_id).filter(Users.chat_id == chat_id))
            user = result.fetchone()
            if user is not None:
                return user[0]
            else:
                return None


async def get_user_username(username, message: types.Message, session_maker: sessionmaker):
    async with session_maker() as session:
        async with session.begin():

            if message.chat.id == message.from_user.id:
                result = await session.execute(
                    select(Users).filter(Users.username == username).filter(Users.chat_id == Users.user_id))
            else:
                result = await session.execute(select(Users).filter(Users.username == username).filter(Users.chat_id == message.chat.id))

            user = result.fetchone()
            if user is not None:
                return user[0]
            else:
                return None


async def add_user(user_id, chat_id, username, name, chat_name, session_maker: sessionmaker):
    async with session_maker() as session:
        async with session.begin():
            user = Users(user_id = user_id, chat_id= chat_id, username = username, name = name, chat_name=chat_name)
            session.add(user)


async def refresh_user(event: types.Message, user: Users, session_maker: sessionmaker):
    async with session_maker() as session:
        async with session.begin():
            today = datetime.date.today()

            if user.username == event.from_user.username and user.name == event.from_user.full_name and user.date == today:

                return None
            delta = today - user.date

            if delta > datetime.timedelta(days=0):
                user.date = today
                user.attack = 3
                user.defense = 3
                user.force = 0

                if delta == datetime.timedelta(days=1):
                    if user.trys < 0:
                        user.grows = 0
                        user.trys += 1
                    else:
                        user.grows = 1

                else:
                    if user.trys < 0:
                        user.trys = 0

                    user.grows = 1

            await session.execute(update(Users)
                                  .where(Users.user_id == event.from_user.id)
                                  .where(Users.chat_id == event.chat.id).values(username=event.from_user.username,
                                                                                name=event.from_user.full_name,
                                                                                chat_name=event.chat.full_name,
                                                                                date=user.date,
                                                                                grows=user.grows,
                                                                                attack=user.attack,
                                                                                defense=user.defense,
                                                                                trys=user.trys))

async def semi_refresh_user(user: Users, session_maker):
    async with session_maker() as session:
        async with session.begin():
            today = datetime.date.today()

            if user.date == today:

                return user

            delta = today - user.date

            if delta > datetime.timedelta(days=0):
                user.date = today
                user.attack = 3
                user.defense = 3
                user.force = 0

                if delta == datetime.timedelta(days=1):
                    if user.trys < 0:
                        user.grows = 0
                        user.trys += 1
                    else:
                        user.grows = 1

                else:
                    if user.trys < 0:
                        user.trys = 0

                    user.grows = 1

            await session.execute(update(Users)
                                  .where(Users.user_id == user.user_id)
                                  .where(Users.chat_id == user.chat_id).values(date=user.date,
                                                                                grows=user.grows,
                                                                                attack=user.attack,
                                                                                defense=user.defense,
                                                                                trys=user.trys))
            return user


async def update_user(user: Users, session_maker: sessionmaker):
    async with session_maker() as session:
        async with session.begin():
            stmt = update(Users).where(Users.user_id == user.user_id, Users.chat_id == user.chat_id)\
                .values(username=user.username,
                        name=user.name,
                        chat_name=user.chat_name,
                        length=user.length,
                        date=user.date,
                        grows=user.grows,
                        attack=user.attack,
                        defense=user.defense,
                        trys=user.trys,
                        force=user.force)

            await session.execute(stmt)


async def get_top(message: types.Message, session_maker: sessionmaker, stop=10, start=0):
    async with session_maker() as session:
        async with session.begin():

            if message.chat.id == message.from_user.id:
                stmt1 = select(Users.user_id, Users.name, Users.length).where(
                    Users.user_id == Users.chat_id).subquery()
            else:
                stmt1 = select(Users.user_id, Users.name, Users.length).where(Users.chat_id == message.chat.id).subquery()

            stmt2 = select(stmt1.c.user_id, stmt1.c.name, stmt1.c.length,
                           func.row_number().over(order_by=desc(stmt1.c.length)).label('row_number')).subquery()
            stmt = select(stmt2.c.user_id, stmt2.c.name, stmt2.c.length, stmt2.c.row_number).where(or_(stmt2.c.user_id == message.from_user.id, and_(
                stmt2.c.row_number <= stop, stmt2.c.row_number > start)))

            result = await session.execute(stmt)
            return result.fetchall()


async def get_user_place(user_id, chat_id, session_maker:sessionmaker):
    async with session_maker() as session:
        async with session.begin():

            if chat_id == user_id:
                stmt1 = select(Users.user_id, Users.name, Users.length).where(
                    Users.chat_id == Users.user_id).subquery()
            else:
                stmt1 = select(Users.user_id, Users.name, Users.length).where(Users.chat_id == chat_id).subquery()

            stmt2 = select(stmt1.c.user_id, stmt1.c.name, stmt1.c.length,
                           func.row_number().over(order_by=desc(stmt1.c.length)).label('row_number')).subquery()
            stmt = select(stmt2.c.user_id, stmt2.c.name, stmt2.c.length, stmt2.c.row_number).where(stmt2.c.user_id == user_id)

            result = await session.execute(stmt)
            return result.fetchone()


async def get_global_top(message: types.Message, session_maker, stop=10, start=0):
    async with (session_maker() as session):
        async with session.begin():

            stmt2 = select(Users.user_id, Users.chat_id, Users.name, Users.chat_name, Users.length,
                           func.row_number().over(order_by=desc(Users.length)).label('row_number')).subquery()
            stmt = select(stmt2.c.user_id, stmt2.c.chat_id, stmt2.c.name, stmt2.c.chat_name, stmt2.c.length, stmt2.c.row_number
                          ).where(or_(and_(stmt2.c.user_id == message.from_user.id, stmt2.c.chat_id == message.chat.id),
                and_(stmt2.c.row_number <= stop, stmt2.c.row_number > start)))

            result = await session.execute(stmt)
            return result.fetchall()


async def get_user_global_place(message: types.Message, session_maker: sessionmaker):
    async with session_maker() as session:
        async with session.begin():

            stmt2 = select(Users.user_id, Users.chat_id, Users.name, Users.chat_name, Users.length,
                           func.row_number().over(order_by=desc(Users.length)).label('row_number')).subquery()
            stmt = select(stmt2.c.user_id, stmt2.c.chat_id, stmt2.c.name, stmt2.c.chat_name, stmt2.c.length, stmt2.c.row_number).where(stmt2.c.user_id == message.from_user.id, stmt2.c.chat_id == message.chat.id)

            result = await session.execute(stmt)
            return result.fetchone()


async def get_count_top(message: types.Message, session_maker: sessionmaker):
    async with session_maker() as session:
        async with session.begin():
            if message.chat.id == message.from_user.id:
                stmt1 = select(count()).select_from(Users).where(Users.chat_id == Users.user_id)
            else:
                stmt1 = select(count()).select_from(Users).where(Users.chat_id == message.chat.id)

            result = await session.execute(stmt1)
            return result.fetchone()[0]


async def get_count_global_top(session_maker: sessionmaker):
    async with session_maker() as session:
        async with session.begin():
            stmt1 = select(count()).select_from(Users)
            result = await session.execute(stmt1)
            return result.fetchone()[0]


# async def add_old_user(user, session_maker: sessionmaker):
#     async with session_maker() as session:
#         async with session.begin():
#             user = Users(user_id = user_id, chat_id= chat_id, username = username, name = name, chat_name=chat_name)
#             session.add(user)


async def clean_chat(chat_id, session_maker: sessionmaker):
    async with session_maker() as session:
        async with session.begin():
            stmt = delete(Users).where(Users.chat_id == chat_id)
            await session.execute(stmt)


async def get_chats(session_maker: sessionmaker):
    async with session_maker() as session:
        async with session.begin():
            stmt = select(Users.chat_id).distinct()
            result = await session.execute(stmt)
            return result.fetchall()

