import emoji
from aiogram import types
from aiogram.fsm.context import FSMContext

from core.services.database import Database
from core.services import wb_parser
from core.keyboards import reply, inline
from core.states import AddProductStates, UpdateProductStates


async def main_menu(msg: types.Message, db: Database, state: FSMContext = None):
    await msg.answer('Меню', reply_markup=reply.main_keyboard(await db.is_admin(msg.from_user.id)))
    if state:
        await state.clear()


async def start(msg: types.Message, db: Database):
    """Команда /start"""
    await msg.answer(
        f'Привет, {msg.from_user.first_name}. '
        'Этот бот будет следить за ценами на товары в Wildberries.',
        reply_markup=reply.main_keyboard(await db.is_admin(msg.from_user.id))
    )
    await db.update_user(msg.from_user.id, msg.from_user.first_name)


async def add_product(msg: types.Message, state: FSMContext):
    """Запрашивает артикул товара для отслеживания цены"""
    await msg.answer(
        'Отправь артикул товара:',
        reply_markup=reply.cancle_keyboard('Артикул')
    )
    await state.set_state(AddProductStates.GET_ARTICLE)


async def add_product_get_article(msg: types.Message, state: FSMContext):
    """Добавляет товар для отслеживания"""
    article = msg.text
    if article and article.isdigit():
        await state.update_data(article=article)
        await msg.answer('Поиск товара...')
        name, price = await wb_parser.get_price(article)
        if name is None or price is None:
            await msg.answer(
                f'{emoji.emojize(":red_circle:")} Не найдено' \
                '\nПопробуй ещё раз',
                reply_markup=reply.cancle_keyboard('Артикул')
            )
            return
        await msg.answer(f'{emoji.emojize(":green_circle:")} Найдено')
        await state.update_data(name=name)
        await state.update_data(price=price)
        await msg.answer(
            f'<b>{name}</b>\n' \
            f'Цена на данный момент: <b>{price}</b> BYN' \
            '\nПродолжить?',
            reply_markup=reply.yes_or_no('Продолжить?')
        )
        await state.set_state(AddProductStates.CONFIRM)
    else:
        await msg.answer(
            'Не похоже на артикул. Вот пример: 234335796' \
            '\nПопробуй ещё раз :)'
        )


async def add_product_confirm(msg: types.Message, state: FSMContext, db: Database):
    """Подвтерждение добавления товара"""
    if msg.text == 'Да':
        await msg.answer(
            'Отлично! Теперь укажи ожидаемую цену (12.34):',
            reply_markup=reply.cancle_keyboard('00.00')
        )
        await state.set_state(AddProductStates.GET_PRICE)
    else:
        await msg.answer('Хорошо, не добавляем.')
        await main_menu(msg, db, state)


async def add_product_get_price(msg: types.Message, state: FSMContext, db: Database):
    """Сохраняет информацию о товаре и желаемой стоимости"""
    desired_price = wb_parser.str_price_to_float(msg.text)
    if desired_price == -1:
        await msg.answer('Не похоже на цену\nПопробуй ещё раз')
        return
    name = await state.get_value('name')
    price = await state.get_value('price')
    article = await state.get_value('article')
    if price <= desired_price:
        await msg.answer('Ожидаемая цена должна быть ниже текущей\nПопробуй ещё раз')
        return
    await db.add_product(
        msg.from_user.id,
        article,
        name,
        desired_price,
        price
    )
    await msg.answer(f'{emoji.emojize(":green_circle:")} Добавлено')
    await main_menu(msg, db, state)


async def tracked_products(msg: types.Message, db: Database):
    """Показывает все отслеживаемые товары пользователя"""
    products = await db.get_user_products(msg.from_user.id)
    if not products:
        await msg.answer('Пока пусто')
        return
    for product in products:
        new_data = await wb_parser.get_price(product.get('article'))
        if new_data[1] is None:
            await msg.answer(
                f'{emoji.emojize(":package:")} {new_data[0] or product.get("name")}\n\n'
                f'{emoji.emojize(":red_exclamation_mark:")} Нет в наличии\n',
                reply_markup=inline.product_keyboard(product.get('id'), only_delete=True)
            )
            return
        await db.update_product(
            product_id=product.get('id'),
            price=new_data[1],
            name=new_data[0]
        )
        price_diff = (int(new_data[1] * 100) - int(product.get('last_price') * 100)) / 100
        if price_diff < 0:
            price_symbol = emoji.emojize(':red_triangle_pointed_down:')
            price_symbol += f' ({price_diff})'
        elif price_diff > 0:
            price_symbol = emoji.emojize(':red_triangle_pointed_up:')
            price_symbol += f' (+{price_diff})'
        else:
            price_symbol = ''
        await msg.answer(
            f'{emoji.emojize(":package:")} {new_data[0]}\n' \
            f'Цена: <b>{new_data[1]}</b> BYN {price_symbol}\n\n' \
            f'Ожидаемая цена: <b>{product.get("desired_price")}</b> BYN',
            reply_markup=inline.product_keyboard(product.get('id'))
        )


async def product_update_request(call: types.CallbackQuery, state: FSMContext):
    """Обновление желаемой цены. Запрашивает новую стоимость"""
    await call.answer()
    await call.message.answer(
        'Новая ожидаемая цена:',
        reply_markup=reply.cancle_keyboard('00.00')
    )
    await state.set_state(UpdateProductStates.GET_NEW_PRICE)
    product_id = call.data.replace('pr_update_', '')
    await state.update_data(product_id=product_id, call=call)


async def product_update_price(msg: types.Message, state: FSMContext, db: Database):
    """Обновление желаемой цены. Сохраняет новую стоимость"""
    call = await state.get_value('call')
    old_text = call.message.text
    old_text_split = old_text.split(' ')
    old_price = old_text_split[old_text_split.index('BYN') - 1]
    desired_price = wb_parser.str_price_to_float(msg.text)
    if desired_price == -1:
        await msg.answer('Не похоже на цену\nПопробуй ещё раз')
        return
    # проверяем ниже ли ожидаемая цена
    if float(old_price) <= desired_price:
        await msg.answer('Ожидаемая цена должна быть ниже текущей\nПопробуй ещё раз')
        return
    old_text_split[-2] = str(desired_price)
    new_text = ' '.join(old_text_split)
    product_id = await state.get_value('product_id')
    await db.update_desired_price(product_id, desired_price)
    await msg.answer(f'{emoji.emojize(":green_circle:")} Цена обновлена')
    await call.message.edit_text(new_text, reply_markup=inline.product_keyboard(product_id))
    await main_menu(msg, db, state)


async def product_delete(call: types.CallbackQuery, db: Database):
    """Удаляет товар из отслеживаемых"""
    await call.answer()
    await call.message.delete()
    product_id = call.data.replace('pr_delete_', '')
    await db.delete_product(product_id)
    await call.message.answer(
        f'{emoji.emojize(":green_circle:")} Удалено'
    )
