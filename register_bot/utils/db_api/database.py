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

    async def check_user(self, telegram_id: str):
        sql = (
            "SELECT is_active, NULL::text AS qr_code, 'gym' AS source "
            "FROM main_app_worker WHERE telegram_id = $1 "
            "UNION ALL "
            "SELECT is_active, qr_code, 'client' AS source "
            "FROM main_app_client WHERE telegram_id = $1 "
            "LIMIT 1;"
        )
        return await self.execute(
            sql,
            telegram_id,
            fetchrow=True,
        )

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
        # SQL_EXAMPLE = "INSERT INTO main_app_client
        # (id, name, surname, username, phone)
        # VALUES(1, 'John', 'Smith', 'jsmith', '+1234567890')"
        sql = (
            "INSERT INTO main_app_client "
            "(user_name, first_name, last_name, telegram_id, phone_number, "
            "language, secret_code, qr_code, is_active) "
            "VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)"
        )
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
        # SQL_EXAMPLE = "SELECT * FROM main_app_client
        # where id=1 AND Name='John'"
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
        # SQL_EXAMPLE = "INSERT INTO main_app_worker
        # (id, name, surname, username, phone)
        # VALUES(1, 'John', 'Smith', 'jsmith', '+1234567890')"
        sql = (
            "INSERT INTO main_app_worker "
            "(gym_id, user_name, first_name, last_name, telegram_id, "
            "phone_number, language, is_director, is_active) "
            "VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)"
        )
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

    async def sort_worker_by_gym(self, telegram_id, **kwargs):
        sql = (
            "SELECT * FROM main_app_worker WHERE gym_id = ( "
            "SELECT gym_id FROM main_app_worker "
            "WHERE telegram_id = $1 AND gym_id IS NOT NULL ) "
            "AND gym_id IS NOT NULL;"
        )
        return await self.execute(
            sql,
            telegram_id,
            fetch=True,
        )

    async def update_worker(self, telegram_id, **kwargs):
        sql = """
        UPDATE main_app_worker
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
        # SQL_EXAMPLE = "INSERT INTO main_app_gym
        # (id, name, surname, username, phone)
        # VALUES(1, 'John', 'Smith', 'jsmith', '+1234567890') RETURNING 1"
        sql = (
            "INSERT INTO main_app_gym "
            "(name, loc_lat, loc_long, secret_code, qr_code, lump_sum, "
            "balance, date_end, is_active) "
            "VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9) "
            "RETURNING id"
        )
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
        # SQL_EXAMPLE = "SELECT * FROM main_app_gym
        # where id=1 AND Name='John'"
        sql = "SELECT * FROM main_app_gym WHERE "
        sql, parameters = self.format_args(sql, " AND ", kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def select_gym_by_worker(self, telegram_id, **kwargs):
        sql = (
            "SELECT g.id AS gym_id, g.loc_lat, g.loc_long, g.lump_sum, "
            "g.waiting_location, g.waiting_lump_sum, g.is_active "
            "FROM main_app_worker w "
            "LEFT JOIN main_app_gym g ON g.id = w.gym_id "
            "WHERE w.telegram_id = $1;"
        )
        return await self.execute(
            sql,
            telegram_id,
            fetchrow=True,
        )

    async def update_gym_by_worker(self, telegram_id, **kwargs):
        sql = """
        UPDATE main_app_gym
        SET """
        sql, parameters = (
            self.format_args(sql, ", ", kwargs)
            if len(kwargs) > 1
            else self.format_args(sql, "", kwargs)
        )
        sql += (
            " WHERE id = ( SELECT gym_id FROM main_app_worker "
            + f"WHERE telegram_id = ${len(kwargs)+1});"
        )
        return await self.execute(
            sql,
            *parameters,
            telegram_id,
            execute=True,
        )

    async def balance_gym(self, telegram_id):
        sql = (
            "SELECT g.id, g.name, g.loc_lat, g.loc_long, "
            "g.balance, g.date_end, g.is_active "
            "FROM main_app_worker w "
            "LEFT JOIN main_app_gym g ON g.id = w.gym_id "
            "WHERE w.telegram_id = $1;"
        )
        return await self.execute(
            sql,
            telegram_id,
            fetchrow=True,
        )

    async def select_payment_for_balance(self, telegram_id):
        sql = (
            "SELECT p.*, g.name, g.loc_lat, g.loc_long FROM main_app_payment p "
            "JOIN main_app_gym g ON g.id = p.gym_id "
            "JOIN main_app_client c ON c.id = p.client_id "
            "WHERE p.is_active = TRUE "
            "AND c.telegram_id = $1 "
            "AND ( "
            "( p.balanse = 0 AND p.date_end IS NOT NULL "
            "AND p.date_end > CURRENT_DATE ) "
            "OR "
            "( p.balanse > 0 AND p.date_end IS NULL "
            "AND p.count < p.balanse ) "
            "OR "
            "( p.balanse > 0 AND p.date_end IS NOT NULL "
            "AND p.date_end >= CURRENT_DATE AND p.count < p.balanse ))"
        )
        return await self.execute(sql, telegram_id, fetch=True)

    async def select_payment_by_month(self, telegram_id, year, month):
        sql = (
            "SELECT p.*, g.name, g.loc_lat, g.loc_long FROM main_app_payment p "
            "JOIN main_app_gym g ON g.id = p.gym_id "
            "JOIN main_app_client c ON c.id = p.client_id "
            "WHERE p.is_active = TRUE "
            "AND c.telegram_id = $1 "
            "AND EXTRACT(YEAR FROM p.date_start) = $2 "
            "AND EXTRACT(MONTH FROM p.date_start) = $3 "
        )
        return await self.execute(sql, telegram_id, year, month, fetch=True)

    async def add_payment_for_lump_sum(self, gym_id, lump_sum):
        sql = (
            "INSERT INTO main_app_payment ( "
            "gym_id, client_id, count, balanse, price, "
            "date_start, date_end, is_trainer, is_active ) "
            "VALUES ($1, NULL, 1, 1, $2, CURRENT_DATE, CURRENT_DATE, FALSE, FALSE) "
            "RETURNING id "
        )
        return await self.execute(sql, gym_id, lump_sum, fetchval=True)

    async def select_registrations_for_client(self, telegram_id, year, month):
        sql = (
            "SELECT r.*, g.name AS gym_name, "
            "g.loc_lat, g.loc_long, p.date_start "
            "FROM main_app_registration r JOIN main_app_client c "
            "ON c.id = r.client_id JOIN main_app_gym g ON g.id = r.gym_id "
            "JOIN main_app_payment p ON p.id = r.payment_id "
            "WHERE c.telegram_id = $1 AND EXTRACT(YEAR FROM r.date) = $2 "
            "AND EXTRACT(MONTH FROM r.date) = $3;"
        )
        return await self.execute(sql, telegram_id, year, month, fetch=True)

    async def select_registrations_by_worker(self, telegram_id, year, month):
        sql = (
            "SELECT r.client_id, "
            "CAST(EXTRACT(DAY FROM r.date) AS INT) AS day "
            "FROM main_app_registration r "
            "JOIN main_app_gym g ON g.id = r.gym_id "
            "JOIN main_app_worker w ON w.gym_id = g.id "
            "WHERE w.telegram_id = $1 "
            "AND EXTRACT(YEAR FROM r.date) = $2 "
            "AND EXTRACT(MONTH FROM r.date) = $3;"
        )
        return await self.execute(sql, telegram_id, year, month, fetch=True)

    async def add_registration_for_lump_sum(self, gym_id, payment_id):
        sql = (
            "INSERT INTO main_app_registration ( "
            "gym_id, client_id, date, is_trainer, payment_id ) "
            "VALUES ($1, NULL, NOW(), FALSE, $2) "
        )
        return await self.execute(sql, gym_id, payment_id, execute=True)

    async def select_admin(self):
        # SQL_EXAMPLE = "SELECT column FROM main_app_admin
        # where id=1 AND Name='John'"
        sql = f"SELECT * FROM main_app_admin"
        return await self.execute(sql, fetchrow=True)


all_tables = AllTables()
