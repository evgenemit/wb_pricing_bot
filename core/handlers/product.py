from aiogram import types
from aiogram.fsm.context import FSMContext

from core.services.database import Database
from core.services import answers, wb_parser
from core.keyboards import reply, inline
from core.states import AddProductStates, UpdateProductStates


async def main_menu(
    msg: types.Message,
    db: Database,
    state: FSMContext = None
) -> None:
    """Возвращает главное меню и очищает state"""
    await msg.answer(
        'Меню',
        reply_markup=reply.main_keyboard(await db.is_admin(msg.from_user.id))
    )
    if state:
        await state.clear()


async def start(msg: types.Message, db: Database) -> None:
    """Команда /start"""
    await msg.answer(
        answers.start_text(msg.from_user.first_name),
        reply_markup=reply.main_keyboard(await db.is_admin(msg.from_user.id))
    )
    await db.update_user(msg.from_user.id, msg.from_user.first_name)


async def add_product(msg: types.Message, state: FSMContext) -> None:
    """Запрашивает артикул товара"""
    await msg.answer(
        'Отправь артикул товара:',
        reply_markup=reply.cancle_keyboard('Артикул')
    )
    await state.set_state(AddProductStates.GET_ARTICLE)


async def add_product_get_article(
    msg: types.Message,
    state: FSMContext
) -> None:
    """Сохраняет артикул, проверяет существует ли товар"""
    article = msg.text
    if not article or not article.isdigit():
        await msg.answer(answers.not_article())
        return
    await state.update_data(article=article)
    await msg.answer('Поиск товара...')
    name, price, count = await wb_parser.get_product_data(article)
    if name is None or price is None:
        await msg.answer(
            answers.product_not_exists(),
            reply_markup=reply.cancle_keyboard('Артикул')
        )
        return
    await msg.answer(answers.product_exists())
    await state.update_data(name=name, price=price, count=count)
    await msg.answer(
        answers.product_confirm(name, price),
        reply_markup=reply.yes_or_no('Продолжить?')
    )
    await state.set_state(AddProductStates.CONFIRM)


async def add_product_confirm(
    msg: types.Message,
    state: FSMContext,
    db: Database
) -> None:
    """Обработка подтверждения добавления товара"""
    if msg.text == 'Да':
        await msg.answer(
            answers.product_confirm_true(),
            reply_markup=reply.cancle_keyboard('00.00')
        )
        await state.set_state(AddProductStates.GET_PRICE)
    else:
        await msg.answer(answers.product_confirm_false())
        await main_menu(msg, db, state)


async def add_product_get_price(
    msg: types.Message,
    state: FSMContext,
    db: Database
) -> None:
    """Сохраняет информацию о товаре и желаемую стоимость в базе"""
    desired_price = wb_parser.parse_price(msg.text)
    if desired_price == -1:
        await msg.answer(answers.not_price())
        return
    name = await state.get_value('name')
    price = await state.get_value('price')
    article = await state.get_value('article')
    count = await state.get_value('count')
    if price <= desired_price:
        await msg.answer(answers.desired_price_not_valid())
        return
    await db.add_product(
        msg.from_user.id, article, name, desired_price, price, count
    )
    await msg.answer(answers.prodcut_added())
    await main_menu(msg, db, state)


async def tracked_products(msg: types.Message, db: Database) -> None:
    """Показывает все отслеживаемые товары пользователя"""
    products = await db.get_user_products(msg.from_user.id)
    if not products:
        await msg.answer('Пока пусто')
        return
    for product in products:
        new_data = await wb_parser.get_product_data(product.article)
        new_name, new_price, count = new_data
        if not count:
            await msg.answer(
                answers.product_not_available(new_name or product.name),
                reply_markup=inline.product_keyboard(
                    product.item_id, only_delete=True
                )
            )
            return
        await db.update_product(
            product_id=product.item_id,
            price=new_price,
            name=new_name,
            count=count
        )
        await msg.answer(
            answers.product_info(
                new_name, new_price, product.last_price,
                product.desired_price, count
            ),
            reply_markup=inline.product_keyboard(product.item_id)
        )


async def product_update_request(
    call: types.CallbackQuery,
    state: FSMContext
) -> None:
    """Обновление желаемой цены. Запрашивает новую стоимость"""
    await call.answer()
    await call.message.answer(
        answers.get_new_desired_price(),
        reply_markup=reply.cancle_keyboard('00.00')
    )
    await state.set_state(UpdateProductStates.GET_NEW_PRICE)
    product_id = call.data.replace('pr_update_', '')
    await state.update_data(product_id=product_id, call=call)


async def product_update_price(
    msg: types.Message,
    state: FSMContext,
    db: Database
) -> None:
    """Обновление желаемой цены. Сохраняет новую стоимость"""
    desired_price = wb_parser.parse_price(msg.text)
    if desired_price == -1:
        await msg.answer(answers.not_price())
        return
    product_id = await state.get_value('product_id')
    product = await db.get_product(product_id)
    # проверяем ниже ли ожидаемая цена
    if product.last_price <= desired_price:
        await msg.answer(answers.desired_price_not_valid())
        return
    if product.desired_price != desired_price:
        call = await state.get_value('call')
        await db.update_desired_price(product_id, desired_price)
        await call.message.edit_text(
            answers.product_info(
                product.name,
                product.last_price,
                product.last_price,
                desired_price,
                product.count
            ),
            reply_markup=inline.product_keyboard(product_id)
        )
    await msg.answer(answers.price_updated())
    await main_menu(msg, db, state)


async def product_delete(call: types.CallbackQuery, db: Database):
    """Удаляет товар из отслеживаемых"""
    await call.answer()
    await call.message.delete()
    product_id = call.data.replace('pr_delete_', '')
    await db.delete_product(product_id)
    await call.message.answer(answers.product_deleted())
