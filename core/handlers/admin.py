import aiofiles
from aiogram import types

from core.handlers.product import main_menu
from core.services.database import Database


async def get_logs(msg: types.Message, db: Database) -> None:
    """Возвращает логи"""
    async with aiofiles.open('logs.txt', 'r') as f:
        text = ''
        async for line in f:
            text += line
            if len(text) > 4000:
                await msg.answer(text)
                text = ''
        if text:
            await msg.answer(text)
        await main_menu(msg, db)
