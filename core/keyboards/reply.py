from aiogram.utils.keyboard import ReplyKeyboardBuilder


def main_keyboard(is_admin: bool):
    """Клавиутрура главного меню"""
    kb = ReplyKeyboardBuilder()
    kb.button(text='Отслеживаемые')
    kb.button(text='Добавить')
    if is_admin:
        kb.button(text='Логи')
    kb.adjust(1)
    return kb.as_markup(
        resize_keyboard=True
    )


def cancle_keyboard(placeholder: str = ''):
    """Кнопка Отмена"""
    kb = ReplyKeyboardBuilder()
    kb.button(text='Отмена')
    kb.adjust(1)
    return kb.as_markup(
        resize_keyboard=True,
        input_field_placeholder=placeholder
    )


def yes_or_no(placeholder: str = ''):
    """Клавиутара Да или Нет"""
    kb = ReplyKeyboardBuilder()
    kb.button(text='Да')
    kb.button(text='Нет')
    kb.button(text='Отмена')
    kb.adjust(2, 1)
    return kb.as_markup(
         resize_keyboard=True,
        input_field_placeholder=placeholder
    )
