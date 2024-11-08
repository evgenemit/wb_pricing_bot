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
            try:
                if data['data']['products']:
                    name = data['data']['products'][0]['name']
                    price = data['data']['products'][0]['sizes'][0]['price']['total']
                    price /= 100
                else:
                    return (None, None)
            except (KeyError, TypeError):
                name = None
                price = None
    return (name, price)


def str_price_to_float(price: str) -> float:
    if not price:
        return -1
    price = price.replace(',', '.').replace(' ', '')
    if not price.replace('.', '').isdigit():
        return -1
    return float(price)
    