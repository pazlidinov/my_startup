from loader import dp
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart

from states.clientData import Client
import logging


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    print(message.from_user)
    # await state.update_data(user_name=message.from_user.username)
    # await state.update_data(first_name=message.from_user.first_name)
    # await state.update_data(last_name=message.from_user.last_name)
    # await state.update_data(telegram_id=message.from_user.id).
    await message.answer(
        "🇺🇿Hurmatli mijoz, kerakli tilni tanlang!\n"
        "🇺🇿Ҳурматли мижоз, керакли тилни танланг!\n"
        "🇷🇺Уважаемый клиент, пожалуйста, выберите нужный язык!"
    )
