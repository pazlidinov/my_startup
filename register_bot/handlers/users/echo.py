from aiogram import types

from loader import dp


# Echo bot
@dp.message_handler(content_types=types.ContentType.TEXT, state=None)
async def bot_echo(message: types.Message):
    await message.answer(message.text)
