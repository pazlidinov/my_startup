from aiogram import types
from aiogram.dispatcher.filters import Command
from utils.db_api.database import all_tables as db
from loader import dp
from keyboards.inline import menu_client, menu_gym
import logging
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
MEDIA_DIR = BASE_DIR / "qr_code_img"
MEDIA_DIR.mkdir(parents=True, exist_ok=True)


@dp.message_handler(Command(commands=["menu"]))
async def menu(message: types.Message):
    await message.delete()
    try:
        user = dict(await db.check_user(telegram_id=str(message.from_user.id)))
        if not user:
            await message.answer(
                "❗ Siz ro'yhatdan o'tmagansiz.\n📋 Iltimos, ro'yhatdan o'ting!"
            )
        if not user["is_active"]:
            await message.answer(
                text="❗ Siz aktiv holatda emassiz.\n"
                + "Agar 👨‍👦‍👦 hodim bo'lsangiz, reseptionga murojaat qiling!\n"
                + "Agar mijoz bo'lsangiz, admin murojaat qiling!"
            )
        if user["source"] == "client":
            await message.answer_photo(
                open(user["qr_code"], "rb"),
                caption="⬆️ QrCodeni reseptionga ko'rsating\n⬇️ Zalning QrCodeni skanerlang",
                reply_markup=menu_client.client_main_menu,
            )
        if user["source"] == "gym":
            await message.answer_photo(
                open(MEDIA_DIR / f"{message.from_user.id}.png", "rb"),
                caption="⬆️ QrCodeni reseptionga ko'rsating\n⬇️ Zalning QrCodeni skanerlang",
                reply_markup=menu_gym.gym_main_menu,
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
