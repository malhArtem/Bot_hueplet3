import datetime
from typing import Callable, Dict, Any, Awaitable, Union

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select, insert, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from db import Users
from db.users import get_user, update_user, add_user, refresh_user
import time


class UpdateData(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Union[Message, CallbackQuery],
        data: Dict[str, Any]
    ) -> Any:

        session_maker: sessionmaker = data['session_maker']
        session: AsyncSession

        user = await get_user(event.from_user.id, event.chat.id, session_maker)
        user: Users

        if user:
            await refresh_user(event, user, session_maker)
        else:
            await add_user(event.from_user.id, event.chat.id, event.from_user.username, event.from_user.full_name, event.chat.full_name, session_maker)
        data['session_maker'] = session_maker

        result = await handler(event, data)

        return result
