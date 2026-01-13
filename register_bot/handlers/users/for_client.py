from datetime import datetime, timedelta
from loader import bot, dp
from aiogram import types
from aiogram.dispatcher import FSMContext
from keyboards.inline import langsKeyboard, roleKeyboard, menu_client, menu_gym
from utils.others.secret_code import generate_code
from utils.others.qr_code import generate_qr_code
from utils.db_api.database import all_tables as db
import logging
import asyncio
import os


@dp.callback_query_handler(lambda c: c.data == "client_new_qrcodeent")
async def for_client(call: types.CallbackQuery):
    try:
        client = await db.select_client(telegram_id=call.from_user.id)
        path_img = client.qr_code
        os.remove(path_img)
        secret_code = await generate_code(10)
        qr_code = generate_qr_code(call.from_user.id, secret_code)
        db.update_client(
            secret_code=secret_code, qr_code=qr_code, telegram_id=call.from_user.id
        )
        await call.message.delete()
        await call.answer(
            "☑️ Tabriklaymiz, QrCode muvaffaqiyatli yangilandi", show_alert=True
        )
        await call.message.answer_photo(
            open(qr_code, "rb"),
            caption="⬆️ QrCodeni reseptionga ko'rsating\n⬇️ Zalning QrCodeni skanerlang",
            reply_markup=menu_client.client_main_menu,
        )
    except Exception as err:
        logging.exception(err)
        await call.answer(
            "❗ Xatolik yuz berdi, iltimos qayta urinib ko'ring.", show_alert=True
        )
