import asyncio
import logging
import ssl

from aiogram import Dispatcher, types, Bot
from aiogram.filters.command import Command
from aiogram.types import FSInputFile
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from sqlalchemy import URL

import handlers.settings_cmd
from handlers.general_cmd import router
from middlewares import update_data
from aiogram.fsm.strategy import FSMStrategy
from aiogram.fsm.storage.redis import Redis, RedisStorage
from db import *
import set_commands

# token = '5854846177:AAEv829WVN5wnRhhPcBpJ8AttzyvTULrUmE'
token = "5990840392:AAEUviQF4zOevPMHcUXLMfLCG0Vkujc-lmk"

WEB_SERVER_HOST = "127.0.0.1"
WEB_SERVER_PORT = 8080

WEBHOOK_PATH = '/webhook'
BASE_WEBHOOK_URL = 'https://bothueplet.ru'
WEBHOOK_SECRET = "my-secret"

admins_id = '517922464'



async def on_startup(bot: Bot):
    # await bot.set_webhook(f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}",
    #                       secret_token=WEBHOOK_SECRET,
    #                       drop_pending_updates=True)
    await set_commands.set_commands(bot)
    await bot.send_message(admins_id, "Бот запущен")

    #
    # await proceed_schemas(async_engine, BaseModel.metadata)


def main():
    redis = Redis()
    # logging.basicConfig(level=logging.ERROR)

    postgres_url = URL.create(
        "postgresql+asyncpg",
        username='bot_hueplet',
        host='localhost',
        password='zxsdcv',
        database='hueplet_db',
        port=5432
    )

    async_engine = create_async_engine(postgres_url)
    session_maker = get_session_maker(async_engine)

    bot = Bot(token, parse_mode='html')

    dp = Dispatcher(storage=RedisStorage(redis=redis), fsm_strategy=FSMStrategy.CHAT)

    dp.include_router(router)
    dp.include_router(handlers.settings_cmd.rout)
    dp.startup.register(on_startup)

    app = web.Application()

    webhook_requests_handler = SimpleRequestHandler(dispatcher=dp,
                                                    bot=bot,
                                                    secret_token=WEBHOOK_SECRET,
                                                    session_maker=session_maker
    )

    webhook_requests_handler.register(app, path=WEBHOOK_PATH)

    setup_application(app, dp, bot=bot)





    # await bot.delete_webhook(drop_pending_updates=True)
    # await dp.start_polling(bot, session_maker=session_maker)
    web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)

async def polling_main():
    redis = Redis()
    # logging.basicConfig(level=logging.ERROR)

    postgres_url = URL.create(
        "postgresql+asyncpg",
        username='bot_hueplet',
        host='localhost',
        password='zxsdcv',
        database='hueplet_db',
        port=5432
    )

    async_engine = create_async_engine(postgres_url)
    session_maker = get_session_maker(async_engine)

    bot = Bot(token, parse_mode='html')

    dp = Dispatcher(storage=RedisStorage(redis=redis), fsm_strategy=FSMStrategy.CHAT)

    dp.include_router(router)
    dp.include_router(handlers.settings_cmd.rout)
    dp.startup.register(on_startup)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, session_maker=session_maker)

if __name__ == '__main__':
    logging.basicConfig(level=logging.ERROR)
    asyncio.run(polling_main())
    # main()

