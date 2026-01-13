from typing import Union
import asyncpg
from asyncpg import Connection
from asyncpg.pool import Pool
from data import config
from typing import Optional
from datetime import date


class AllTables:
    def __init__(self):
        self.pool: Union[Pool, None] = None

    async def connect(self):
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
    def format_args(sql, addition: str, parameters: dict):
        sql += addition.join(
            [f"{item} = ${i}" for i, item in enumerate(parameters, start=1)]
        )
        return sql, tuple(parameters.values())

    async def add_client(
        self,
        user_name: str,
        first_name: str,
        last_name: str,
        telegram_id: str,
        phone_number: str,
        language: str,
        secret_code: str,
        qr_code: str,
        is_active: bool = True,
    ):
        # SQL_EXAMPLE = "INSERT INTO main_app_client(id, name, surname, username, phone) VALUES(1, 'John', 'Smith', 'jsmith', '+1234567890')"

        sql = """
        INSERT INTO main_app_client (user_name, first_name, last_name, telegram_id, phone_number, language, secret_code, qr_code, is_active) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        """
        return await self.execute(
            sql,
            user_name,
            first_name,
            last_name,
            telegram_id,
            phone_number,
            language,
            secret_code,
            qr_code,
            is_active,
            execute=True,
        )

    async def select_client(self, **kwargs):
        # SQL_EXAMPLE = "SELECT * FROM main_app_client where id=1 AND Name='John'"
        sql = "SELECT * FROM main_app_client WHERE "
        sql, parameters = self.format_args(sql, " AND ", kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def update_client(self, telegram_id, **kwargs):
        sql = """
        UPDATE main_app_client
        SET """
        sql, parameters = (
            self.format_args(sql, ", ", kwargs)
            if len(kwargs) > 1
            else self.format_args(sql, "", kwargs)
        )
        sql += f" WHERE telegram_id = ${len(kwargs)+1}"

        return await self.execute(
            sql,
            *parameters,
            telegram_id,
            execute=True,
        )

    async def add_worker(
        self,
        gym: int,
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
        INSERT INTO main_app_worker (gym_id, user_name, first_name, last_name, telegram_id, phone_number, language, is_director, is_active) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        """
        return await self.execute(
            sql,
            gym,
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
        sql, parameters = self.format_args(sql, " AND ", kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def add_gym(
        self,
        name: str,
        loc_lat: float,
        loc_long: float,
        secret_code: str,
        qr_code: str,
        lump_sum: int,
        balance: int = 0,
        date_end: Optional[date] = None,
        is_active: bool = True,
    ):
        # SQL_EXAMPLE = "INSERT INTO main_app_gym(id, name, surname, username, phone) VALUES(1, 'John', 'Smith', 'jsmith', '+1234567890')"

        sql = """
        INSERT INTO main_app_gym (name, loc_lat, loc_long, secret_code, qr_code, lump_sum, balance, date_end, is_active) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9) RETURNING id
        """
        return await self.execute(
            sql,
            name,
            loc_lat,
            loc_long,
            secret_code,
            qr_code,
            lump_sum,
            balance,
            date_end,
            is_active,
            fetchval=True,
        )

    async def select_gym(self, **kwargs):
        # SQL_EXAMPLE = "SELECT * FROM main_app_gym where id=1 AND Name='John'"
        sql = "SELECT * FROM main_app_gym WHERE "
        sql, parameters = self.format_args(sql, " AND ", kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def select_admin(self, column, **kwargs):
        # SQL_EXAMPLE = "SELECT column FROM main_app_admin where id=1 AND Name='John'"
        sql = f"SELECT {column} FROM main_app_admin"
        return await self.execute(sql, fetchval=True)


all_tables = AllTables()
