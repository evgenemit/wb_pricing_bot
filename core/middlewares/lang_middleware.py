import redis
import asyncpg
from typing import Callable, Awaitable, Dict, Any
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update

from core.services.database import Database


class LangMiddleware(BaseMiddleware):
    def __init__(
        self,
        redis: redis.Redis,
        pool_connect: asyncpg.Pool
    ) -> None:
        self.r = redis
        self.connection = pool_connect

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        try:
            uid = event.message.from_user.id
        except:
            pass
        try:
            uid = event.callback_query.from_user.id
        except:
            pass
        if uid:
            if self.r.exists(f'u_{uid}'):
                lang = self.r.get(f'u_{uid}')
                data['lang'] = lang
            else:
                db = Database(self.connection)
                print(uid)
                lang = await db.get_user_lang(uid)
                self.r.set(f'u_{uid}', lang)
                data['lang'] = lang
        return await handler(event, data)
