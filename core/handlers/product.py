import emoji
from aiogram import types
from aiogram.fsm.context import FSMContext

from core.services.database import Database
from core.services import wb_parser
from core.keyboards import reply, inline
from core.states import AddProductStates, UpdateProductStates

from core.services.answers import answers, product_info


async def main_menu(
    msg: types.Message,
    db: Database,
    lang: str,
    state: FSMContext = None
) -> None:
    """Возвращает главное меню и очищает state"""
    await msg.answer(
        answers[lang]['t2'],
        reply_markup=reply.main_keyboard(
            await db.is_admin(msg.chat.id), lang
        )
    )
    if state:
        await state.clear()


async def start(msg: types.Message, db: Database, lang: str) -> None:
    """Команда /start"""
    await msg.answer(
        answers[lang]['t1'].format(name=msg.from_user.first_name),
        reply_markup=reply.main_keyboard(
            await db.is_admin(msg.from_user.id), lang
        )
    )
    await db.update_user(msg.from_user.id, msg.from_user.first_name)


async def add_product(msg: types.Message, state: FSMContext, lang: str) -> None:
    """Запрашивает артикул товара"""
    await msg.answer(
        answers[lang]['t3'],
        reply_markup=reply.cancle_keyboard(lang, answers[lang]['ph1'])
    )
    await state.set_state(AddProductStates.GET_ARTICLE)


async def add_product_get_article(
    msg: types.Message,
    state: FSMContext,
    lang: str
) -> None:
    """Сохраняет артикул, проверяет существует ли товар"""
    article = msg.text
    if not article or not article.isdigit():
        await msg.answer(answers[lang]['t4'])
        return
    await state.update_data(article=article)
    await msg.answer(answers[lang]['t5'])
    name, price, count = await wb_parser.get_product_data(article)
    if name is None or price is None:
        await msg.answer(
            answers[lang]['t6'].format(emoji=emoji.emojize(":red_circle:")),
            reply_markup=reply.cancle_keyboard(lang, answers[lang]['ph1'])
        )
        return
    await msg.answer(
        answers[lang]['t7'].format(emoji=emoji.emojize(":green_circle:"))
    )
    await state.update_data(name=name, price=price, count=count)
    await msg.answer(
        answers[lang]['t8'].format(name=name, price=price),
        reply_markup=reply.yes_or_no(lang, answers[lang]['ph2'])
    )
    await state.set_state(AddProductStates.CONFIRM)


async def add_product_confirm(
    msg: types.Message,
    state: FSMContext,
    db: Database,
    lang: str
) -> None:
    """Обработка подтверждения добавления товара"""
    if msg.text == answers[lang]['btn4']:
        await msg.answer(
            answers[lang]['t9'],
            reply_markup=reply.cancle_keyboard(lang, answers[lang]['ph3'])
        )
        await state.set_state(AddProductStates.GET_PRICE)
    else:
        await msg.answer(answers[lang]['t10'])
        await main_menu(msg, db, lang, state)


async def add_product_get_price(
    msg: types.Message,
    state: FSMContext,
    db: Database,
    lang: str
) -> None:
    """Сохраняет информацию о товаре и желаемую стоимость в базе"""
    desired_price = wb_parser.parse_price(msg.text)
    if desired_price == -1:
        await msg.answer(answers[lang]['t11'])
        return
    name = await state.get_value('name')
    price = await state.get_value('price')
    article = await state.get_value('article')
    count = await state.get_value('count')
    if price <= desired_price:
        await msg.answer(answers[lang]['t12'])
        return
    await db.add_product(
        msg.from_user.id, article, name, desired_price, price, count
    )
    await msg.answer(answers[lang]['t13'].format(
        emoji=emoji.emojize(":green_circle:")
    ))
    await main_menu(msg, db, lang, state)


async def tracked_products(msg: types.Message, db: Database, lang: str) -> None:
    """Показывает все отслеживаемые товары пользователя"""
    products = await db.get_user_products(msg.from_user.id)
    if not products:
        await msg.answer(answers[lang]['t14'])
        return
    for product in products:
        new_data = await wb_parser.get_product_data(product.article)
        new_name, new_price, count = new_data
        if not count:
            await msg.answer(
                answers[lang]['t15'].format(
                    emoji1=emoji.emojize(":package:"),
                    name=new_name or product.name,
                    emoji2=emoji.emojize(":red_exclamation_mark:")
                ),
                reply_markup=inline.product_keyboard(
                    lang, product.item_id, only_delete=True
                )
            )
            continue
        await db.update_product(
            product_id=product.item_id,
            price=new_price,
            name=new_name,
            count=count
        )
        await msg.answer(
            product_info(
                new_name, new_price, product.last_price,
                product.desired_price, count, lang
            ),
            reply_markup=inline.product_keyboard(lang, product.item_id)
        )


async def product_update_request(
    call: types.CallbackQuery,
    state: FSMContext,
    lang: str
) -> None:
    """Обновление желаемой цены. Запрашивает новую стоимость"""
    await call.answer()
    await call.message.answer(
        answers[lang]['t17'],
        reply_markup=reply.cancle_keyboard(lang, answers[lang]['ph3'])
    )
    await state.set_state(UpdateProductStates.GET_NEW_PRICE)
    product_id = call.data.replace('pr_update_', '')
    await state.update_data(product_id=product_id, call=call)


async def product_update_price(
    msg: types.Message,
    state: FSMContext,
    db: Database,
    lang: str
) -> None:
    """Обновление желаемой цены. Сохраняет новую стоимость"""
    desired_price = wb_parser.parse_price(msg.text)
    if desired_price == -1:
        await msg.answer(answers[lang]['t11'])
        return
    product_id = await state.get_value('product_id')
    product = await db.get_product(product_id)
    # проверяем ниже ли ожидаемая цена
    if product.last_price <= desired_price:
        await msg.answer(answers[lang]['t12'])
        return
    if product.desired_price != desired_price:
        call = await state.get_value('call')
        await db.update_desired_price(product_id, desired_price)
        await call.message.edit_text(
            product_info(
                product.name,
                product.last_price,
                product.last_price,
                desired_price,
                product.count,
                lang
            ),
            reply_markup=inline.product_keyboard(lang, product_id)
        )
    await msg.answer(answers[lang]['t18'].format(
        emoji=emoji.emojize(":green_circle:")
    ))
    await main_menu(msg, db, lang, state)


async def product_delete(
    call: types.CallbackQuery,
    db: Database,
    lang: str
) -> None:
    """Удаляет товар из отслеживаемых"""
    await call.answer()
    await call.message.delete()
    product_id = call.data.replace('pr_delete_', '')
    await db.delete_product(product_id)
    await call.message.answer(answers[lang]['t19'].format(
        emoji=emoji.emojize(":green_circle:")
    ))


async def settings(msg: types.Message, lang: str) -> None:
    """Показывает доступные настройки"""
    await msg.answer(
        answers[lang]['t23'],
        reply_markup=inline.lang_settings()
    )


async def lang_settings(call: types.CallbackQuery, db: Database) -> None:
    """Устанавливает для пользователя выбранный язык"""
    await call.answer()
    await call.message.delete()
    lang = call.data.replace('lang_', '')
    await db.update_user_lang(lang, call.from_user.id)
    await call.message.answer(answers[lang]['t24'])
    await main_menu(call.message, db, lang)
