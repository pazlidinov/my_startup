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
            return await message.answer(
                "❗ Siz ro'yhatdan o'tmagansiz.\n📋 Iltimos, ro'yhatdan o'ting!"
            )
        elif not user["is_active"]:
            return await message.answer(
                text="❗ Siz aktiv holatda emassiz.\n"
                + "Agar 👨‍👦‍👦 hodim bo'lsangiz, reseptionga murojaat qiling!\n"
                + "Agar mijoz bo'lsangiz, adminga murojaat qiling!"
            )
        elif user["source"] == "client":
            return await message.answer_photo(
                open(user["qr_code"], "rb"),
                caption="⬆️ QrCodeni reseptionga ko'rsating\n⬇️ Zalning QrCodeni skanerlang",
                reply_markup=menu_client.client_main_menu,
            )
        elif user["source"] == "gym":
            try:
                await db.update_gym_by_worker(
                    telegram_id=str(message.from_user.id),
                    waiting_lump_sum=False,
                    waiting_location=False,
                )
            except Exception as err:
                logging.exception(err)
                await message.answer(
                    "❗ Xatolik yuz berdi, iltimos qayta urinib ko'ring."
                )
            return await message.answer_photo(
                open(MEDIA_DIR / f"{message.from_user.id}.png", "rb"),
                caption="⬆️ QrCodeni mijozga ko'rsating\n⬇️ Mijozning QrCodeni skanerlang",
                reply_markup=menu_gym.gym_main_menu,
            )
        else:
            return await message.answer(
                "❗ Xatolik yuz berdi, iltimos qayta urinib ko'ring."
            )
    except Exception as err:
        logging.exception(err)
        return await message.answer(
            "❗ Xatolik yuz berdi, iltimos qayta urinib ko'ring."
        )


@dp.callback_query_handler(lambda c: c.data.startswith("menu_"))
async def menu_for_all(call: types.CallbackQuery):
    await call.answer()
    await call.message.delete()
    user_type = call.data.split("_")[-1]
    if user_type == "client":
        return await call.message.answer_photo(
            open(MEDIA_DIR / f"{call.from_user.id}.png", "rb"),
            caption="⬆️ QrCodeni reseptionga ko'rsating\n⬇️ Zalning QrCodeni skanerlang",
            reply_markup=menu_client.client_main_menu,
        )
    elif user_type == "gym":
        return await call.message.answer_photo(
            open(MEDIA_DIR / f"{call.from_user.id}.png", "rb"),
            caption="⬆️ QrCodeni mijozga ko'rsating\n⬇️ Mijozning QrCodeni skanerlang",
            reply_markup=menu_gym.gym_main_menu,
        )
    else:
        return await call.answer("❗ Xatolik yuz berdi, iltimos qayta urinib ko'ring.")
