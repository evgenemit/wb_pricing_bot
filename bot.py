import asyncio
import asyncpg
import logging
import redis
from environs import Env
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from core.router import core_router
from core.services.database import Database
from core.middlewares.lang_middleware import LangMiddleware


logging.basicConfig(level=logging.INFO)
env = Env()
env.read_env('.env')

bot = Bot(
    token=env.str('TOKEN'),
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)


async def main():
    pool_connect = await asyncpg.create_pool(env.str('DB_URI'))
    redis_connect = redis.Redis(
        host='localhost',
        port=6379,
        decode_responses=True
    )
    dp = Dispatcher(
        db=Database(pool_connect)
    )
    dp.include_router(core_router)
    dp.update.middleware(LangMiddleware(redis_connect, pool_connect))

    try:
        await dp.start_polling(bot)
    finally:
        await pool_connect.close()
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())
