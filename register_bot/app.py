from aiogram import executor

from loader import dp
import middlewares, filters, handlers
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands
from utils.db_api.client_table import client_db
from utils.db_api.worker_table import worker_db
from utils.db_api.gym_table import gym_db
from utils.db_api.admin_table import admin_db


async def on_startup(dispatcher):
    await client_db.create()
    await worker_db.create()
    await gym_db.create()
    await admin_db.create()

    # Birlamchi komandalar (/star va /help)
    await set_default_commands(dispatcher)

    # Bot ishga tushgani haqida adminga xabar berish
    await on_startup_notify(dispatcher)


if __name__ == "__main__":
    executor.start_polling(dp, on_startup=on_startup)
