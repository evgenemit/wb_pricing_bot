from aiogram.utils.keyboard import InlineKeyboardBuilder


def product_keyboard(product_id: int):
    kb = InlineKeyboardBuilder()
    kb.button(text='Изменить цену', callback_data=f'pr_update_{product_id}')
    kb.button(text='Удалить', callback_data=f'pr_delete_{product_id}')
    return kb.as_markup()
