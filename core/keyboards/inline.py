from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup

from core.services.wb_parser import create_wb_link
from core.services.answers import answers


def product_keyboard(
        lang: str,
        product_id: int,
        only_delete: bool = False
) -> InlineKeyboardMarkup:
    """Клавиатура дял карточки товара"""
    kb = InlineKeyboardBuilder()
    if not only_delete:
        kb.button(
            text=answers[lang]['btn6'],
            callback_data=f'pr_update_{product_id}'
        )
    kb.button(
        text=answers[lang]['btn7'],
        callback_data=f'pr_delete_{product_id}'
    )
    return kb.as_markup()


def open_on_wb_keyboard(lang: str, article: str) -> InlineKeyboardMarkup:
    """Клавиатура с кнопкой Открыть на WB"""
    kb = InlineKeyboardBuilder()
    kb.button(text=answers[lang]['btn8'], url=create_wb_link(article))
    return kb.as_markup()


def lang_settings() -> InlineKeyboardMarkup:
    """Клавиаутра для выбора языка"""
    kb = InlineKeyboardBuilder()
    kb.button(text='Русский', callback_data='lang_ru')
    kb.button(text='Беларуская', callback_data='lang_by')
    return kb.as_markup()
