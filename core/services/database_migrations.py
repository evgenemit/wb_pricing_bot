import asyncio
import asyncpg
from environs import Env

from database import Database


async def create_tables():
    env = Env()
    env.read_env('.env')

    pool_connect = await asyncpg.create_pool(env.str('DB_URI'))
    db = Database(pool_connect)
    await db.execute(
        """
        ALTER TABLE products ADD COLUMN notification BOOLEAN DEFAULT false;
        ALTER TABLE products ADD COLUMN count INTEGER DEFAULT 0;
        """
    )
    await pool_connect.close()


if __name__ == '__main__':
    asyncio.run(create_tables())
