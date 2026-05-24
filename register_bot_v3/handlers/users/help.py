from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

router = Router()


@router.message(Command("help"))
async def bot_help(message: Message):
    text = (
        "Buyruqlar:",
        "/start - Botni ishga tushirish",
        "/menu - Menu",
        "/help - Yordam",
    )

    await message.answer("\n".join(text))
