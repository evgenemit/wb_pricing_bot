import emoji
import toml
from decimal import Decimal


answers = toml.load('./core/services/answers.toml')


def product_info(
    name: str,
    price: Decimal,
    last_price: Decimal,
    desired_price: Decimal,
    count: int,
    lang: str
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
    return answers[lang]['t16'].format(
        emoji=emoji.emojize(":package:"),
        name=name, price=price, price_symbol=price_symbol,
        count=count, desired_price=desired_price
    )
