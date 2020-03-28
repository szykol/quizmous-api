import asyncio
import asyncpg

class DB:
    _pool: asyncpg.pool.Pool = None

    @staticmethod
    async def init(dsn, *args, **kwargs):
        DB._pool = await asyncpg.create_pool(dsn=dsn, *args, **kwargs)

    @staticmethod
    def get_pool() -> asyncpg.pool.Pool:
        return DB._pool