import emoji
from decimal import Decimal


def start_text(name: str) -> str:
    """Текст команды /start"""
    return (
        f'Привет, {name}. '
        'Этот бот будет следить за ценами на товары в Wildberries.'
    )


def price_fall(name: str, price: Decimal) -> str:
    """Уведомление снижения цены"""
    return (
        f'{emoji.emojize(":check_mark_button:")} '
        'ЦЕНА СНИЗИЛАСЬ!'
        f'\n{name}\n\n<b>{price}</b> BYN'
    )


def price_fall_new_desired(price: Decimal) -> str:
    """Автоматическое обновление ожидаемой цены"""
    return (
        'Ожидаемая цена автоматически снижена на 5%'
        f'\nНовая цена: <b>{price}</b> BYN'
    )


def product_count(count: int, name: str, price: Decimal) -> str:
    """Уведомление о маленьком количестве товара"""
    return (
        f'{emoji.emojize(":red_exclamation_mark:")} '
        f'В наличии всего: <b>{count}</b> шт.'
        f'\n{name}\n\n<b>{price}</b> BYN'
    )


def not_article() -> str:
    """Ошибка валидации артикула"""
    return (
        'Не похоже на артикул. Вот пример: 234335796'
        '\nПопробуй ещё раз :)'
    )


def product_not_exists() -> str:
    """Товар не найден"""
    return f'{emoji.emojize(":red_circle:")} Не найдено \nПопробуй ещё раз'


def product_exists() -> str:
    """Товар найден"""
    return f'{emoji.emojize(":green_circle:")} Найдено'


def product_confirm(name: str, price: Decimal) -> str:
    """Информация о товаре для подтверждения"""
    return (
        f'<b>{name}</b>\n'
        f'Цена на данный момент: <b>{price}</b> BYN \nПродолжить?'
    )


def product_confirm_true() -> str:
    """Добавление товара подтверждено"""
    return 'Отлично! Теперь укажи ожидаемую цену (12.34):'


def product_confirm_false() -> str:
    """Добавление товара не подтверждено"""
    return 'Хорошо, не добавляем.'


def prodcut_added() -> str:
    """Товар сохранен в базу данных"""
    return f'{emoji.emojize(":green_circle:")} Добавлено'


def not_price() -> str:
    """Некорректная цена"""
    return 'Не похоже на цену\nПопробуй ещё раз'


def product_not_available(name: str) -> str:
    """Товара нет в наличии"""
    return (
        f'{emoji.emojize(":package:")} {name}\n\n'
        f'{emoji.emojize(":red_exclamation_mark:")} Нет в наличии\n'
    )


def product_info(
    name: str,
    price: Decimal,
    last_price: Decimal,
    desired_price: Decimal,
    count: int
) -> str:
    """Карточка товара"""
    price_diff = price - last_price
    price_symbol = ''
    if price_diff < 0:
        price_symbol = emoji.emojize(':red_triangle_pointed_down:')
        price_symbol += f' ({price_diff})'
    elif price_diff > 0:
        price_symbol = emoji.emojize(':red_triangle_pointed_up:')
        price_symbol += f' (+{price_diff})'
    return (
        f'{emoji.emojize(":package:")} {name}\n'
        f'Цена: <b>{price}</b> BYN {price_symbol}\n'
        f'<i>В наличии: {count} шт.</i>\n\n'
        f'Ожидаемая цена: <b>{desired_price}</b> BYN'
    )


def get_new_desired_price() -> str:
    """Запрос новой ожидаемой цены"""
    return 'Новая ожидаемая цена:'


def desired_price_not_valid() -> str:
    """Ожидаемая цена выше цены товара"""
    return 'Ожидаемая цена должна быть ниже текущей\nПопробуй ещё раз'


def price_updated() -> str:
    """Успешное обновление цены"""
    return f'{emoji.emojize(":green_circle:")} Цена обновлена'


def product_deleted() -> str:
    """Успешное удаление товара"""
    return f'{emoji.emojize(":green_circle:")} Удалено'
