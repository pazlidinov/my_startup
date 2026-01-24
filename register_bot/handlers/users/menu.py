from aiogram import types
from aiogram.dispatcher.filters import Command
from utils.db_api.database import all_tables as db
from loader import dp
from keyboards.inline import menu_client
import logging
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
MEDIA_DIR = BASE_DIR / "qr_code_img"
MEDIA_DIR.mkdir(parents=True, exist_ok=True)


@dp.message_handler(Command(commands=["menu"]))
async def menu(message: types.Message):
    await message.delete()
    try:
        client = await db.select_client(telegram_id=str(message.from_user.id))
        await message.answer_photo(
            open(client["qr_code"], "rb"),
            caption="⬆️ QrCodeni reseptionga ko'rsating\n⬇️ Zalning QrCodeni skanerlang",
            reply_markup=menu_client.client_main_menu,
        )        
    except Exception as err:
        logging.exception(err)
        await message.answer("❗ Xatolik yuz berdi, iltimos qayta urinib ko'ring.")


@dp.callback_query_handler(lambda c: c.data == "menu_client")
async def menu_for_client(call: types.CallbackQuery):
    await call.answer()
    await call.message.delete()
    await call.message.answer_photo(
        open(MEDIA_DIR / f"{call.from_user.id}.png", "rb"),
        caption="⬆️ QrCodeni reseptionga ko'rsating\n⬇️ Zalning QrCodeni skanerlang",
        reply_markup=menu_client.client_main_menu,
    )
