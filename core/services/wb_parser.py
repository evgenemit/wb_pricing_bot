import aiohttp


async def get_product_data(article: str) -> tuple:
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
                name = data['data']['products'][0]['name']
            except (KeyError, IndexError):
                name = None
            try:
                price = data['data']['products'][0]['sizes'][0]['price']['total']
                price /= 100
            except (KeyError, TypeError, IndexError):
                price = None
            try:
                count = data['data']['products'][0]['totalQuantity']
            except (KeyError, IndexError):
                count = None
    return name, price, count


def parse_price(price: str) -> float:
    if not price:
        return -1
    price = price.replace(',', '.').replace(' ', '')
    if not price.replace('.', '').isdigit():
        return -1
    return float(price)
