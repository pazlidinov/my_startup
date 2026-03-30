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
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


@dp.callback_query_handler(lambda c: c.data == "gym_balance")
async def client_active_balance(call: types.CallbackQuery):
    await call.answer()
    group_link_key = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔎 Skanerlash", callback_data="client_scaner"
                ),
            ],
        ]
    )
    try:
        info_gym = dict(await db.balance_gym(telegram_id=str(call.from_user.id)))
        info_admin = await db.select_admin()
        group_link_key = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Guruhga kirish",
                        url=info_admin["gym_group_link"],
                    ),
                ],
            ]
        )
        await call.message.answer(
            text=f"<b>✏️ <a href='https://maps.google.com/?q={info_gym['loc_lat']},{info_gym['loc_long']}'>{info_gym['name']}</a></b>\n"
            + f"<b>🆔 ID:</b> {info_gym['id']}\n"
            + f"<b>💲 Balans:</b> {info_gym['balance']} so'm\n"
            + f"<b>🗓️ Muddati:</b> {info_gym['date_end']}\n"
            + f"<b>⭕ Faolligi:</b> {'✅ Foal' if info_gym['is_active'] else '❌ Foal emas'}"
            + f"\n\n\n"
            + f"<b>💲 To'lov uchun:</b>\n"
            + f"{info_admin['card_number']}\n"
            + f"{info_admin['card_name']}\n"
            + f"<b>💶 Oylik to'lov:</b> {info_admin['amount']} so'm\n\n"
            + f"<b>ℹ️ Eslatma:</b> To'lov cheki va zal 🆔 ID\n"
            + f"quyidagi guruhga yuboring\n",
            reply_markup=group_link_key,
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
    except Exception as err:
        logging.exception(err)
        await call.message.answer("❗ Xatolik yuz berdi, iltimos qayta urinib ko'ring.")


@dp.callback_query_handler(lambda c: c.data == "gym_settings")
async def client_active_balance(call: types.CallbackQuery):
    await call.answer()
    try:
        await db.update_gym_by_worker(
            telegram_id=str(call.from_user.id),
            waiting_lump_sum=False,
            waiting_location=False,
        )
    except Exception as err:
        logging.exception(err)
        await call.message.answer("❗ Xatolik yuz berdi, iltimos qayta urinib ko'ring.")
    await call.message.delete()
    await call.message.answer(
        text="⚙️ Sozlamalar", reply_markup=menu_gym.gym_settings_menu
    )
