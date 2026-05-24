from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode 
from aiogram.fsm.storage.memory import MemoryStorage

from data import config


bot = Bot(token=config.BOT_TOKEN)

storage = MemoryStorage()

dp = Dispatcher(storage=storage)
