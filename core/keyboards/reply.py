from aiogram.utils.keyboard import ReplyKeyboardBuilder

from core.services.answers import answers


def main_keyboard(is_admin: bool, lang: str):
    """Клавиутрура главного меню"""
    kb = ReplyKeyboardBuilder()
    kb.button(text=answers[lang]['btn1'])
    kb.button(text=answers[lang]['btn2'])
    kb.button(text=answers[lang]['btn9'])
    if is_admin:
        kb.button(text='Логи')
        kb.button(text='Отправить сообщение')
    kb.adjust(1)
    return kb.as_markup(
        resize_keyboard=True
    )


def cancle_keyboard(lang: str, placeholder: str = ''):
    """Кнопка Отмена"""
    kb = ReplyKeyboardBuilder()
    kb.button(text=answers[lang]['btn3'])
    kb.adjust(1)
    return kb.as_markup(
        resize_keyboard=True,
        input_field_placeholder=placeholder
    )


def yes_or_no(lang: str, placeholder: str = ''):
    """Клавиутара Да или Нет"""
    kb = ReplyKeyboardBuilder()
    kb.button(text=answers[lang]['btn4'])
    kb.button(text=answers[lang]['btn5'])
    kb.button(text=answers[lang]['btn3'])
    kb.adjust(2, 1)
    return kb.as_markup(
        resize_keyboard=True,
        input_field_placeholder=placeholder
    )
