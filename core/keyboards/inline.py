from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup

from core.services.wb_parser import create_wb_link


def product_keyboard(
        product_id: int,
        only_delete: bool = False
) -> InlineKeyboardMarkup:
    """Клавиатура дял карточки товара"""
    kb = InlineKeyboardBuilder()
    if not only_delete:
        kb.button(
            text='Изменить цену',
            callback_data=f'pr_update_{product_id}'
        )
    kb.button(text='Удалить', callback_data=f'pr_delete_{product_id}')
    return kb.as_markup()


def open_on_wb_keyboard(article: str) -> InlineKeyboardMarkup:
    """Клавиатура с кнопкой Открыть на WB"""
    kb = InlineKeyboardBuilder()
    kb.button(text='Открыть на WB', url=create_wb_link(article))
    return kb.as_markup()
