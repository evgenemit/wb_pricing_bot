import emoji
from decimal import Decimal


def price_fall(name: str, price: Decimal) -> str:
    """Текст уведомления снижения цены"""
    return (
        f'{emoji.emojize(":check_mark_button:")} '
        'ЦЕНА СНИЗИЛАСЬ!'
        f'\n{name}\n\n<b>{price}</b> BYN'
    )


def price_fall_new_desired(price: Decimal) -> str:
    """Текст автоматического обновления ожидаемой цены"""
    return (
        'Ожидаемая цена автоматически снижена на 5%'
        f'\nНовая цена: <b>{price}</b> BYN'
    )


def product_count(count: int, name: str, price: Decimal) -> str:
    """Текст уведомления о маленьком количестве товара"""
    return (
        f'{emoji.emojize(":red_exclamation_mark:")} '
        f'В наличии всего: <b>{count}</b> шт.'
        f'\n{name}\n\n<b>{price}</b> BYN'
    )
