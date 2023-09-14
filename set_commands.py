from aiogram import Bot

from aiogram.types import BotCommand, BotCommandScopeDefault, BotCommandScopeAllChatAdministrators, BotCommandScopeAllPrivateChats


async def set_commands(bot: Bot):
    commands = [
        BotCommand(
            command='huy',
            description='Вырастить писюндрий'
        ),
        BotCommand(
            command='battle',
            description='Скрестить шпаги'
        ),
        BotCommand(
            command='top',
            description='Топ чата'
        ),
        BotCommand(
            command='global_top',
            description='Глобальный топ'
        ),
        BotCommand(
            command='profile',
            description='Посмотреть профиль'
        ),
        BotCommand(
            command='help',
            description='Помощь'
        )
    ]

    admin_commands = [
        BotCommand(
            command='huy',
            description='Вырастить писюндрий'
        ),
        BotCommand(
            command='battle',
            description='Скрестить шпаги'
        ),
        BotCommand(
            command='top',
            description='Топ чата'
        ),
        BotCommand(
            command='global_top',
            description='Глобальный топ'
        ),
        BotCommand(
            command='profile',
            description='Посмотреть профиль'
        ),
        BotCommand(
            command='settings',
            description='Настройки бота'
        ),
        BotCommand(
            command='help',
            description='Помощь'
        )
    ]

    ls_commands = [
        BotCommand(
            command='huy',
            description='Вырастить писюндрий'
        ),
        BotCommand(
            command='battle',
            description='Скрестить шпаги'
        ),
        BotCommand(
            command='top',
            description='Топ чата'
        ),
        BotCommand(
            command='global_top',
            description='Глобальный топ'
        ),
        BotCommand(
            command='profile',
            description='Посмотреть профиль'
        ),
        BotCommand(
            command='bot_to_group',
            description='Добавить бота в чат'
        ),
        BotCommand(
            command='help',
            description='Помощь'
        )
    ]

    await bot.set_my_commands(admin_commands, BotCommandScopeAllChatAdministrators())
    await bot.set_my_commands(commands, BotCommandScopeDefault())
    await bot.set_my_commands(ls_commands, BotCommandScopeAllPrivateChats())