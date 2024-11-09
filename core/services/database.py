import asyncpg


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

    async def get_admins(self) -> tuple:
        admins_ids = await self.fetch("SELECT tg_user_id FROM admins;")
        return tuple(map(lambda x: x.get('tg_user_id'), admins_ids))


    async def is_admin(self, tg_user_id) -> bool:
        """Проверяет является ли пользователем администратором"""
        user_is_admin = await self.fetchrow(
            f"""
            SELECT EXISTS
            (SELECT 1 FROM admins WHERE tg_user_id = '{tg_user_id}');
            """
        )
        return user_is_admin.get('exists', False)


    async def update_user(self, tg_user_id: int, first_name: str) -> bool:
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
            last_price: float
    ) -> None:
        """Сохраняет информацию о товаре"""
        await self.execute(
            f"""
            INSERT INTO products
            (user_id, article, name, desired_price, last_price)
            VALUES (
            (SELECT id FROM users WHERE tg_user_id = '{tg_user_id}'),
            '{article}', '{name}', {desired_price}, {last_price});
            """
        )

    async def get_all_products(self) -> dict:
        """Все товары всех пользователей"""
        products = await self.fetch(
            "SELECT id, user_id, article, desired_price FROM products;"
        )
        data = {}
        for product in products:
            user_id = product.get('user_id')
            if user_id not in data:
                data[user_id] = []
            data[user_id].append(
                (product.get('id'), product.get('article'), product.get('desired_price'))
            )
        return data

    async def get_tg_user_id(self, user_id: int) -> str:
        """Возвращает телеграм id пользователя по id в таблице"""
        user = await self.fetchrow(
            f"SELECT tg_user_id FROM users WHERE id = {user_id};"
        )
        return user.get('tg_user_id')

    async def get_user_products(self, tg_user_id: str) -> list:
        """Возвращает список всех товаров пользователя"""
        products = await self.fetch(
            f"""
            SELECT * FROM products WHERE
            user_id = (SELECT id FROM users WHERE tg_user_id = '{tg_user_id}')
            ORDER BY id;
            """
        )
        return products

    async def update_product(self, product_id: int, price: float, name: str) -> None:
        """Обновляет информацию о товаре"""
        await self.execute(
            f"""
            UPDATE products SET
            last_price = {price}, name = '{name}'
            WHERE id = {product_id};
            """
        )

    async def update_desired_price(self, product_id: str, desired_price: float) -> None:
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
