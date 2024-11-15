import aiohttp
from decimal import Decimal


async def get_product_data(
        article: str
) -> tuple[str | None, Decimal | None, int | None]:
    async with aiohttp.ClientSession() as session:
        # получаем данные геолокации (xinfo) для запроса информации о товаре
        async with session.get(
            'https://user-geo-data.wildberries.ru/get-geo-info'
            '?currency=BYN&latitude=53.9007&longitude=27.5709&'
            'locale=by&address=Минск&dt=0'
        ) as response:
            data = await response.json()
            xinfo = data.get('xinfo')

        # получаем информацию о товаре
        async with session.get(
            'https://card.wb.ru/cards/v2/detail?'
            f'{xinfo}&ab_testing=false&nm={article}'
        ) as response:
            data = await response.json()
            try:
                data = data['data']['products'][0]
            except (KeyError, IndexError):
                return None, None, None
            name = data.get('name')
            count = data.get('totalQuantity')
            try:
                price = data['sizes'][0]['price']['total']
                price /= 100
                price = Decimal(str(price))
            except (KeyError, IndexError, TypeError):
                price = None
    return name, price, count


def parse_price(price: str) -> Decimal | int:
    if not price or type(price) != str:
        return -1
    price = price.replace(',', '.').replace(' ', '')
    if not price.replace('.', '').isdigit():
        return -1
    if '.' not in price:
        price += '.0'
    return Decimal(price)
