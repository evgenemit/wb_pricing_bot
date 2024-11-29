from aiogram.fsm.state import State, StatesGroup


class AddProductStates(StatesGroup):
    """Добавление товара"""
    GET_ARTICLE = State()
    CONFIRM = State()
    GET_PRICE = State()


class UpdateProductStates(StatesGroup):
    """Обновление желаемой цены товара"""
    GET_NEW_PRICE = State()


class SendMessage(StatesGroup):
    """Отправка сообщения всем пользователям"""
    GET_TEXT = State()
