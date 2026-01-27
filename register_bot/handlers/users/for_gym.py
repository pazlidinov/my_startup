from datetime import date
from loader import dp
from aiogram import types
from keyboards.inline import langsKeyboard, menu_gym, monthsKeyboard
from utils.others.secret_code import generate_code
from utils.others.qr_code import generate_qr_code
from utils.db_api.database import all_tables as db
import logging
import os
from pathlib import Path
from aiogram.types import InlineKeyboardButton


@dp.callback_query_handler(lambda c: c.data == "gym_balance")
async def client_active_balance(call: types.CallbackQuery):
    await call.answer()
    try:
        info_gym = dict(await db.balance_gym(telegram_id=str(call.from_user.id)))
        await call.message.answer(
            text=f"<b><a href='https://maps.google.com/?q={info_gym['loc_lat']},{info_gym['loc_long']}'>{info_gym['name']}</a></b>\n"
            + f"<b>💲 Balans:</b> {info_gym['balance']} so'm\n"
            + f"<b>🗓️ Muddati:</b> {info_gym['date_end']}\n"
            + f"<b>⭕ Faolligi:</b> {'☑️ Foal' if info_gym['is_active'] else '❌ Foal emas'}\n",
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
    except Exception as err:
        logging.exception(err)
        await call.answer(
            "❗ Xatolik yuz berdi, iltimos qayta urinib ko'ring.", show_alert=True
        )


@dp.callback_query_handler(lambda c: c.data == "gym_settings")
async def client_active_balance(call: types.CallbackQuery):
    await call.answer()
    await call.message.delete()
    await call.message.answer(
        text="⚙️ Sozlamalar", reply_markup=menu_gym.gym_settings_menu
    )
