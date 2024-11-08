import asyncio
import asyncpg
import logging
from environs import Env
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from core.router import core_router
from core.services.database import Database


logging.basicConfig(level=logging.INFO)
env = Env()
env.read_env('.env')

bot = Bot(
    token=env.str('TOKEN'),
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)


async def main():
    pool_connect = await asyncpg.create_pool(env.str('DB_URI'))
    dp = Dispatcher(
        db=Database(pool_connect)
    )
    dp.include_router(core_router)

    try:
        await dp.start_polling(bot)
    finally:
        await pool_connect.close()
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())
