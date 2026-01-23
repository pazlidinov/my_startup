from aiogram import types
from aiogram.dispatcher.filters import Command
from utils.db_api.database import all_tables as db
from loader import dp
from keyboards.inline import menu_client
import logging


@dp.message_handler(Command(commands=["menu"]))
async def menu(message: types.Message):
    try:
        client = await db.select_client(telegram_id=str(message.from_user.id))
        await message.delete()
        await message.answer_photo(
            open(client["qr_code"], "rb"),
            caption="⬆️ QrCodeni reseptionga ko'rsating\n⬇️ Zalning QrCodeni skanerlang",
            reply_markup=menu_client.client_main_menu,
        )
    except Exception as err:
        logging.exception(err)
        await message.answer(
            "❗ Xatolik yuz berdi, iltimos qayta urinib ko'ring.", show_alert=True
        )
