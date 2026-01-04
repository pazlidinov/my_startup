from typing import Union
import asyncpg
from asyncpg import Connection
from asyncpg.pool import Pool
from data import config
from datetime import date
from typing import Optional


class AdminDatabase:
    def __init__(self):
        self.pool: Union[Pool, None] = None

    async def create(self):
        self.pool = await asyncpg.create_pool(
            user=config.DB_USER,
            password=config.DB_PASS,
            host=config.DB_HOST,
            database=config.DB_NAME,
            port=config.DB_PORT,
        )

    async def execute(
        self,
        command,
        *args,
        fetch: bool = False,
        fetchval: bool = False,
        fetchrow: bool = False,
        execute: bool = False,
    ):
        async with self.pool.acquire() as connection:
            connection: Connection
            async with connection.transaction():
                if fetch:
                    result = await connection.fetch(command, *args)
                elif fetchval:
                    result = await connection.fetchval(command, *args)
                elif fetchrow:
                    result = await connection.fetchrow(command, *args)
                elif execute:
                    result = await connection.execute(command, *args)
                return result

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join(
            [f"{item} = ${i}" for i, item in enumerate(parameters, start=1)]
        )
        return sql, tuple(parameters.values())

    async def select_admin(self, column, **kwargs):
        # SQL_EXAMPLE = "SELECT column FROM main_app_admin where id=1 AND Name='John'"
        sql = f"SELECT {column} FROM main_app_admin WHERE "
        sql, parameters = self.format_args(sql, kwargs)
        sql += " LIMIT 1"
        return await self.execute(sql, *parameters, fetchval=True)


admin_db = AdminDatabase()
