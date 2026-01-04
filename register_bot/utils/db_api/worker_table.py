from typing import Union
import asyncpg
from asyncpg import Connection
from asyncpg.pool import Pool
from data import config


class WorkerDatabase:
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

    async def add_worker(
        self,
        user_name: str,
        first_name: str,
        last_name: str,
        telegram_id: str,
        phone_number: str,
        language: str,
        is_director: bool = False,
        is_active: bool = True,
    ):
        # SQL_EXAMPLE = "INSERT INTO main_app_worker(id, name, surname, username, phone) VALUES(1, 'John', 'Smith', 'jsmith', '+1234567890')"

        sql = """
        INSERT INTO main_app_worker (user_name, first_name, last_name, telegram_id, phone_number, language, is_director, is_active) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        """
        return await self.execute(
            sql,
            user_name,
            first_name,
            last_name,
            telegram_id,
            phone_number,
            language,
            is_director,
            is_active,
            execute=True,
        )

    async def select_worker(self, **kwargs):
        # SQL_EXAMPLE = "SELECT * FROM main_app_worker where id=1 AND Name='John'"
        sql = "SELECT * FROM main_app_worker WHERE "
        sql, parameters = self.format_args(sql, kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)


worker_db = WorkerDatabase()
