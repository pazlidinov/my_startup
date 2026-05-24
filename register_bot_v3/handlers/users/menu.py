from utils.db_api.database import all_tables as db
from keyboards.inline import menu_client, menu_gym
import logging
from pathlib import Path
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile, ReplyKeyboardRemove
from aiogram.filters import Command
from .start import bot_start

router = Router()
BASE_DIR = Path(__file__).resolve().parent.parent.parent
MEDIA_DIR = BASE_DIR / "qr_code_img"
MEDIA_DIR.mkdir(parents=True, exist_ok=True)


@router.callback_query(F.data.startswith("menu_"))
async def menu_for_all(call: CallbackQuery):
    await call.answer()
    await call.message.delete()
    await call.message.answer(".", reply_markup=ReplyKeyboardRemove())
    user_type = call.data.split("_")[-1]
    if user_type == "client":
        return await call.message.answer_photo(
            photo=FSInputFile(MEDIA_DIR / f"{call.from_user.id}.png"),
            caption="⬆️ QrCodeni reseptionga ko'rsating\n⬇️ Zalning QrCodeni skanerlang",
            reply_markup=menu_client.client_main_menu,
        )
    elif user_type == "gym":
        return await call.message.answer_photo(
            photo=FSInputFile(MEDIA_DIR / f"{call.from_user.id}.png"),
            caption="⬆️ QrCodeni mijozga ko'rsating\n⬇️ Mijozning QrCodeni skanerlang",
            reply_markup=menu_gym.gym_main_menu,
        )
    else:
        return await call.answer("❗ Xatolik yuz berdi, iltimos qayta urinib ko'ring.")
