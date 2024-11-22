import aiofiles
import asyncio
import datetime
from aiogram import Bot

from core.services import wb_parser, answers
from core.services.database import Database
from core.keyboards.inline import open_on_wb_keyboard


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


async def update_all_prices(bot: Bot, db: Database):
    while True:
        await add_logs('Проверются цены')
        data = await db.get_all_products()
        for user_id in data:
            tg_user_id = await db.get_tg_user_id(user_id)
            for product in data[user_id]:
                new_data = await wb_parser.get_product_data(product.article)
                if not all(new_data):
                    continue
                new_name, new_price, count = new_data
                await db.update_product(
                    product.item_id, product.last_price, new_name, count
                )
                if new_price <= product.desired_price:
                    await add_logs(
                        f'Цена снижена: {new_price=} article={product.article}'
                    )
                    await bot.send_message(
                        tg_user_id,
                        answers.price_fall(new_name, new_price),
                        reply_markup=open_on_wb_keyboard(product.article)
                    )
                    new_desired_price = int(new_price * 95) / 100
                    await db.update_desired_price(
                        product.item_id,
                        new_desired_price
                    )
                    await bot.send_message(
                        tg_user_id,
                        answers.price_fall_new_desired(new_desired_price)
                    )
                if count > 0 and count <= 3 and not product.notification:
                    await bot.send_message(
                        tg_user_id,
                        answers.product_count(count, new_name, new_price)
                    )
                    await db.update_product_notification(
                        product.item_id, True
                    )
                elif product.notification and count > 3:
                    await db.update_product_notification(
                        product.item_id, False
                    )

        await add_logs('Проверены')
        await asyncio.sleep(60 * 30)


async def delete_logs():
    """Удаляет логи"""
    async with aiofiles.open('logs.txt', 'w') as f:
        await f.write(f'[{datetime.datetime.now()}] Логи удалены\n')
    await asyncio.sleep(60 * 60 * 24 * 7)
