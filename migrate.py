import asyncio

from sqlalchemy import URL

from db import create_async_engine, get_session_maker, proceed_schemas, BaseModel
from db.users import Users, add_user
import sqlite3
import datetime
bd = sqlite3.connect('pop.db')
cur = bd.cursor()


def get_profile(chat_id):
    cur.execute("SELECT * FROM '{}' "
                .format(chat_id))
    temp = cur.fetchall()

    return temp


def get_chat_id():
    cur.execute("SELECT * FROM sqlite_master WHERE type = 'table'")
    return cur.fetchall()


async def main():
    postgres_url = URL.create(
        "postgresql+asyncpg",
        username='bot_hueplet',
        host='localhost',
        password='zxsdcv',
        database='hueplet_db',
        port=5432)

    async_engine = create_async_engine(postgres_url)
    session_maker = get_session_maker(async_engine)
    chats = get_chat_id()

    await proceed_schemas(async_engine, BaseModel.metadata)


    for chat in chats:
        if chat[1] != 'global':
            profiles = get_profile(chat[1])
            chat_name = cur.execute("SELECT chat_name FROM global WHERE chat_id = '{}' ".format(chat[1])).fetchone()
            for profile in profiles:
                print(profile)
                user = Users(user_id=int(profile[0]),
                             chat_id=int(chat[1]),
                             username=profile[1],
                             name=profile[2],
                             date=datetime.datetime.strptime(profile[4], "%Y-%m-%d"),
                             length=profile[3],
                             grows=profile[5],
                             attack=profile[6],
                             defense=profile[7],
                             force=profile[9],
                             trys=profile[8],
                             chat_name=chat_name[0])

                async with session_maker() as session:
                    async with session.begin():
                        session.add(user)

if __name__ == '__main__':
    asyncio.run(main())