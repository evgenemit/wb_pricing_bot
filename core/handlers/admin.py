import aiofiles
from aiogram import types, Bot
from aiogram.fsm.context import FSMContext

from core.handlers.product import main_menu
from core.services.database import Database
from core.keyboards.reply import cancle_keyboard
from core.states import SendMessage


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


async def get_message(msg: types.Message, db: Database, state: FSMContext) -> None:
    """Запрашивает текст сообщения"""
    is_admin = await db.is_admin(msg.chat.id)
    if not is_admin:
        return
    await msg.answer('Сообщение:', reply_markup=cancle_keyboard('ru'))
    await state.set_state(SendMessage.GET_TEXT)


async def send_message(msg: types.Message, bot: Bot, db: Database, state: FSMContext) -> None:
    """Отправляет текст всем пользователям"""
    users = await db.get_all_users_ids()
    text = msg.text
    for user in users:
        await bot.send_message(user, text)
    lang = await db.get_user_lang(msg.chat.id)
    await main_menu(msg, db, lang, state)
