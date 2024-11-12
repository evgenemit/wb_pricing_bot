import aiofiles
import asyncio
import emoji
import datetime
from aiogram import Bot

from core.services import wb_parser
from core.services.database import Database


async def add_logs(text: str):
    """Записывает логи в файл"""
    async with aiofiles.open('logs.txt', 'a') as f:
        await f.write(
            f'[{datetime.datetime.now()}] {text}\n'
        )


async def startup(bot: Bot, db: Database):
    """Запуск бота"""
    asyncio.create_task(delete_logs())
    await asyncio.sleep(1)
    await add_logs('Бот запущен')
    asyncio.create_task(update_all_prices(bot, db))


async def shutdown():
    """Завершение работы бота"""
    await add_logs('Бот остановлен')


async def update_all_prices(bot: Bot, db: Database):
    while True:
        await add_logs('Проверются цены')
        data = await db.get_all_products()
        for user_id in data:
            tg_user_id = await db.get_tg_user_id(user_id)
            products = data[user_id]
            for product in products:
                new_name, new_price, _ = await wb_parser.get_product_data(product[1])
                if new_name is None or new_price is None:
                    await add_logs(f'Пропущен {product[1]}')
                    continue
                if new_price <= product[2]:
                    await add_logs(f'Цена снижена: {user_id=} {new_price=} {product[2]=}')
                    await bot.send_message(
                        tg_user_id,
                        f'{emoji.emojize(":check_mark_button:")} ЦЕНА СНИЗИЛАСЬ!' \
                        f'\n{new_name}\n\n<b>{new_price}</b> BYN'
                    )
                    new_desired_price = int(new_price * 95) / 100
                    await db.update_desired_price(product[0], new_desired_price)
                    await bot.send_message(
                        tg_user_id,
                        'Ожидаемая цена автоматически снижена на 5%'\
                        f'\nНовая цена: <b>{new_desired_price}</b> BYN'
                    )
        await add_logs('Проверены')
        await asyncio.sleep(60 * 30)


async def delete_logs():
    """Удаляет логи"""
    async with aiofiles.open('logs.txt', 'w') as f:
        await f.write(f'[{datetime.datetime.now()}] Логи удалены\n')
    await asyncio.sleep(60 * 60 * 24 * 7)
