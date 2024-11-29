import asyncpg
import redis
from pydantic import BaseModel
from decimal import Decimal


class Product(BaseModel):
    item_id: int
    user_id: int
    article: str
    name: str
    desired_price: Decimal
    last_price: Decimal
    notification: bool
    count: int


class Database:

    def __init__(self, pool_connect: asyncpg.pool.Pool) -> None:
        self.connect = pool_connect

    async def execute(self, text: str) -> None:
        async with self.connect.acquire() as connect:
            await connect.execute(text)

    async def fetch(self, text: str) -> list:
        async with self.connect.acquire() as connect:
            return await connect.fetch(text)

    async def fetchrow(self, text: str) -> asyncpg.Record:
        async with self.connect.acquire() as connect:
            return await connect.fetchrow(text)

    async def is_admin(self, tg_user_id) -> bool:
        """Проверяет является ли пользователем администратором"""
        user_is_admin = await self.fetchrow(
            f"""
            SELECT EXISTS
            (SELECT 1 FROM admins WHERE tg_user_id = '{tg_user_id}');
            """
        )
        return user_is_admin.get('exists', False)

    async def update_user(self, tg_user_id: int, first_name: str) -> None:
        """Сохраняет информацию о пользователе"""
        await self.execute(
            f"""
            INSERT INTO users (tg_user_id, first_name)
            VALUES ('{tg_user_id}', '{first_name}')
            ON CONFLICT (tg_user_id)
            DO UPDATE SET first_name = '{first_name}';
            """
        )

    async def add_product(
        self,
        tg_user_id: int,
        article: str,
        name: str,
        desired_price: float,
        last_price: float,
        count: int
    ) -> None:
        """Сохраняет информацию о товаре"""
        await self.execute(
            f"""
            INSERT INTO products
            (user_id, article, name, desired_price, last_price, count)
            VALUES (
            (SELECT id FROM users WHERE tg_user_id = '{tg_user_id}'),
            '{article}', '{name}', {desired_price}, {last_price}, {count});
            """
        )

    async def get_all_products(self) -> dict[int, list[Product]]:
        """
        Формирует словарь, где ключ - id пользователя,
        а значение - список товаров этого пользователя
        """
        products = await self.fetch("SELECT id AS item_id, * FROM products;")
        products = tuple(map(lambda x: Product(**x), products))
        data = {}
        for product in products:
            if product.user_id not in data:
                data[product.user_id] = []
            data[product.user_id].append(product)
        return data

    async def update_product_notification(
        self,
        product_id: int,
        value: bool = True
    ) -> None:
        """Изменяет поле уведомлений для товара по его id"""
        await self.execute(
            f"""
            UPDATE products SET
            notification = {value} WHERE id = {product_id};
            """
        )

    async def get_tg_user_id(self, user_id: int) -> str:
        """Возвращает телеграм id пользователя по id в таблице"""
        user = await self.fetchrow(
            f"SELECT tg_user_id FROM users WHERE id = {user_id};"
        )
        return user.get('tg_user_id')

    async def get_user_products(self, tg_user_id: str) -> tuple[Product]:
        """Возвращает список всех товаров пользователя"""
        products = await self.fetch(
            f"""
            SELECT id AS item_id, * FROM products WHERE
            user_id = (SELECT id FROM users WHERE tg_user_id = '{tg_user_id}')
            ORDER BY id;
            """
        )
        return tuple(map(lambda x: Product(**x), products))

    async def update_product(
        self,
        product_id: int,
        price: float,
        name: str,
        count: int
    ) -> None:
        """Обновляет информацию о товаре"""
        await self.execute(
            f"""
            UPDATE products SET
            last_price = {price}, name = '{name}', count = {count}
            WHERE id = {product_id};
            """
        )

    async def update_desired_price(
        self,
        product_id: str,
        desired_price: float
    ) -> None:
        """Обновляет желаемую стоимость товара"""
        await self.execute(
            f"""
            UPDATE products SET
            desired_price = {desired_price}
            WHERE id = {product_id};
            """
        )

    async def delete_product(self, product_id: str) -> None:
        """Удаляет товар"""
        await self.execute(f"DELETE FROM products WHERE id = {product_id};")

    async def get_product(self, product_id: str) -> Product:
        """Возвращает товар"""
        return Product(**(await self.fetchrow(
            f"SELECT id AS item_id, * FROM products WHERE id = {product_id};"
        )))

    async def get_user_lang(self, tg_user_id: int) -> str:
        """Возвращает язык пользователя"""
        user = await self.fetchrow(
            f"SELECT lang FROM users WHERE tg_user_id = '{tg_user_id}';"
        )
        if user is None:
            return 'ru'
        return user.get('lang')

    async def update_user_lang(self, lang: str, user_id: int) -> None:
        """Обновляет язык пользователя"""
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        r.set(f'u_{user_id}', lang)
        await self.execute(
            f"""
            UPDATE users SET lang = '{lang}' WHERE tg_user_id = '{user_id}';
            """
        )

    async def get_all_users_ids(self) -> list:
        """Возвращает список telegram id всех пользователей"""
        users = await self.fetch("SELECT tg_user_id FROM users;")
        return list(map(lambda x: x.get('tg_user_id'), users))
