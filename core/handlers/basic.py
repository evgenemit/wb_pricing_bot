import asyncio
import emoji
from aiogram import Bot

from core.services import wb_parser
from core.services.database import Database


async def send_for_admins(text: str, bot: Bot, db: Database):
    """Отправляет сообщение всем администраторам"""
    admins_ids = await db.get_admins()
    for admin_id in admins_ids:
        await bot.send_message(admin_id, text)


async def startup(bot: Bot, db: Database):
    """Запуск бота"""
    await send_for_admins('Бот запущен!', bot, db)
    asyncio.create_task(update_all_prices(bot, db))


async def shutdown(bot: Bot, db: Database):
    """Завершение работы бота"""
    await send_for_admins('Бот остановлен!', bot, db)


async def update_all_prices(bot: Bot, db: Database):
    while True:
        data = await db.get_all_products()
        for user_id in data:
            products = data[user_id]
            for product in products:
                new_name, new_price = await wb_parser.get_price(product[1])
                if new_price <= product[2]:
                    tg_user_id = await db.get_tg_user_id(user_id)
                    await bot.send_message(
                        tg_user_id,
                        f'{emoji.emojize(":check_mark_button:")} ЦЕНА СНИЗИЛАСЬ!' \
                        f'\n{new_name}\n\n<b>{new_price}</b> BYN'
                    )
                    new_desired_price = int(product[2] * 95) / 100
                    await db.update_desired_price(product[0], new_desired_price)
                    await bot.send_message(
                        tg_user_id,
                        'Ожидаемая цена автоматически снижена на 5%'\
                        f'\nНовая цена: <b>{new_desired_price}</b> BYN'
                    )
        await asyncio.sleep(60 * 60 * 2)
