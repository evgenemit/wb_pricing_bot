import aiohttp


async def get_price(article: str) -> tuple:
    async with aiohttp.ClientSession() as session:
        async with session.get(
            'https://user-geo-data.wildberries.ru/get-geo-info'
            '?currency=BYN&latitude=53.9007&longitude=27.5709&'
            'locale=by&address=Минск&dt=0'
        ) as response:
            data = await response.json()
            xinfo = data.get('xinfo')

        async with session.get(
            'https://card.wb.ru/cards/v2/detail?'
            f'{xinfo}&ab_testing=false&nm={article}'
        ) as response:
            data = await response.json()
            name = None
            price = None
            try:
                name = data['data']['products'][0]['name']
            except (KeyError, TypeError):
                pass
            try:
                price = data['data']['products'][0]['sizes'][0]['price']['total']
                price /= 100
            except (KeyError, TypeError):
                pass
    return (name, price)


def str_price_to_float(price: str) -> float:
    if not price:
        return -1
    price = price.replace(',', '.').replace(' ', '')
    if not price.replace('.', '').isdigit():
        return -1
    return float(price)
    