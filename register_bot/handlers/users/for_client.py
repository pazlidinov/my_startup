from datetime import date
from loader import dp
from aiogram import types
from keyboards.inline import langsKeyboard, menu_client, monthsKeyboard
from utils.others.secret_code import generate_code
from utils.others.qr_code import generate_qr_code
from utils.db_api.database import all_tables as db
import logging
import os
from pathlib import Path
from aiogram.types import InlineKeyboardButton


BASE_DIR = Path(__file__).resolve().parent.parent.parent
MEDIA_DIR = BASE_DIR / "qr_code_img"
MEDIA_DIR.mkdir(parents=True, exist_ok=True)
all_months = [
    "Yanvar",
    "Fevral",
    "Mart",
    "Aprel",
    "May",
    "Iyun",
    "Iyul",
    "Avgust",
    "Sentabr",
    "Oktyabr",
    "Noyabr",
    "Dekabr",
]


@dp.callback_query_handler(lambda c: c.data == "client_new_qrcode")
async def new_qr_code_for_client(call: types.CallbackQuery):
    try:
        client = await db.select_client(telegram_id=str(call.from_user.id))
        path_img = client["qr_code"]
        os.remove(path_img)
        secret_code = await generate_code(10)
        qr_code = generate_qr_code(call.from_user.id, secret_code)
        await db.update_client(
            telegram_id=str(call.from_user.id), secret_code=secret_code, qr_code=qr_code
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
        await call.answer("❗ Xatolik yuz berdi, iltimos qayta urinib ko'ring.")


@dp.callback_query_handler(lambda c: c.data == "client_balance")
async def client_active_balance(call: types.CallbackQuery):
    await call.answer()
    try:
        client_balance = await db.select_payment_for_balance(
            telegram_id=str(call.from_user.id)
        )
    except Exception as err:
        logging.exception(err)
        return await call.answer("❗ Xatolik yuz berdi, iltimos qayta urinib ko'ring.")
    await call.message.delete()
    if client_balance == []:
        return await call.answer("🚫 Aktiv to'lovlar topilmadi")
    send_text = "Faol bo'lgan to'lovlar:\n"
    for i, item in enumerate(client_balance, start=1):
        send_text += (
            f"<b>{i}) <a href='https://maps.google.com/?q="
            + f"{item['loc_lat']},{item['loc_long']}'>{item['name']}</a></b>\n"
            + f"<b>💵 To'lov:</b> {item['price']}\n"
            + f"<b>📝 Foydalanilgan:</b> {item['count']}/{item['balanse']}\n"
            + f"<b>🗓️ Muddati:</b> {item['date_start']} / {item['date_end']}\n"
            + f"<b>⭕ Faolligi:</b> {'✅ Foal' if item['is_active'] else '❌ Foal emas'}\n"
        )
    await call.message.answer(
        text=send_text,
        parse_mode="HTML",
        disable_web_page_preview=True,
        reply_markup=monthsKeyboard.get_months_key("client", "balance"),
    )


@dp.callback_query_handler(lambda c: c.data.startswith("client_balance_month"))
async def client_balance_by_month(call: types.CallbackQuery):
    await call.answer()
    data_date = call.data.split("_")[-1]
    year = data_date.split("-")[0]
    month = data_date.split("-")[1]
    try:
        client_balance = await db.select_payment_by_month(
            telegram_id=str(call.from_user.id), year=int(year), month=int(month)
        )
    except Exception as err:
        logging.exception(err)
        return await call.answer("❗ Xatolik yuz berdi, iltimos qayta urinib ko'ring.")
    await call.message.delete()
    if len(client_balance) == 0:
        return await call.message.answer(
            text=f"🚫 {year}-yil {all_months[int(month)-1]} oyida to'lovlar topilmadi",
            reply_markup=monthsKeyboard.get_months_key("client", "balance"),
        )
    send_text = f"{year}-yil {all_months[int(month)-1]} oyidagi to'lovlar:\n"
    for i, item in enumerate(client_balance, start=1):
        send_text += (
            f"<b>{i}) <a href='https://maps.google.com/?q={item['loc_lat']},{item['loc_long']}'>{item['name']}</a></b>\n"
            + f"<b>💵 To'lov:</b> {item['price']}\n"
            + f"<b>📝 Foydalanilgan:</b> {item['count']}/{item['balanse']}\n"
            + f"<b>🗓️ Muddati:</b> {item['date_start']} / {item['date_end']}\n"
            + f"<b>⭕ Faolligi:</b> {'☑️ Foal' if item['is_active'] else '❌ Foal emas'}\n"
        )
    return await call.message.answer(
        text=send_text,
        parse_mode="HTML",
        disable_web_page_preview=True,
        reply_markup=monthsKeyboard.get_months_key("client", "balance"),
    )


@dp.callback_query_handler(lambda c: c.data.startswith("client_statistics"))
async def client_statistics(call: types.CallbackQuery):
    await call.answer()
    if len(call.data.split("_")) == 2:
        today = date.today()
        year, month = today.year, today.month
    else:
        data_date = call.data.split("_")
        year = data_date[-1].split("-")[0]
        month = data_date[-1].split("-")[1]
    try:
        client_statistics = await db.select_registrations_for_client(
            telegram_id=str(call.from_user.id), year=int(year), month=int(month)
        )
    except Exception as err:
        logging.exception(err)
        return await call.answer("❗ Xatolik yuz berdi, iltimos qayta urinib ko'ring.")
    await call.message.delete()
    if len(client_statistics) == 0:
        return await call.message.answer(
            text=f"🚫 {year}-yil {all_months[int(month)-1]} oyida foallik topilmadi",
            reply_markup=monthsKeyboard.get_months_key("client", "statistics"),
        )
    send_text = f"{year}-yil {all_months[int(month)-1]} oyidagi faollik:\n"
    for i, item in enumerate(client_statistics, start=1):
        send_text += (
            f"<b>{i}) <a href='https://maps.google.com/?q={item['loc_lat']},{item['loc_long']}'>{item['gym_name']}</a></b>\n"
            + f"<b>🗓️ Sana:</b> {item['date'].strftime('%Y-%m-%d %H:%M:%S')}\n"
            + f"<b>💵 To'lov:</b> {item['date_start']} kungi to'lov asosida\n"
        )
    return await call.message.answer(
        text=send_text,
        parse_mode="HTML",
        disable_web_page_preview=True,
        reply_markup=monthsKeyboard.get_months_key("client", "statistics"),
    )


@dp.callback_query_handler(lambda c: c.data == "client_change_lang")
async def choose_client_lang(call: types.CallbackQuery):
    await call.answer()
    await call.message.delete()
    langs_for_client = langsKeyboard.langs("client")
    await call.message.answer(
        "🇺🇿Hurmatli mijoz, kerakli tilni tanlang!\n"
        "🇺🇿Ҳурматли мижоз, керакли тилни танланг!\n"
        "🇷🇺Уважаемый клиент, пожалуйста, выберите нужный язык!",
        reply_markup=langs_for_client.add(
            InlineKeyboardButton(text="🔙 Menu", callback_data="menu_client")
        ),
    )


@dp.callback_query_handler(lambda c: c.data.startswith("client_lang"))
async def change_client_lang(call: types.CallbackQuery):
    await call.answer()
    try:
        await db.update_client(
            telegram_id=str(call.from_user.id), language=call.data.split("_")[-1]
        )
        await call.message.delete()
        await call.answer("☑️ Tabriklaymiz, til muvaffaqiyatli yangilandi")
        await call.message.answer_photo(
            open(MEDIA_DIR / f"{call.from_user.id}.png", "rb"),
            caption="⬆️ QrCodeni reseptionga ko'rsating\n⬇️ Zalning QrCodeni skanerlang",
            reply_markup=menu_client.client_main_menu,
        )
    except Exception as err:
        logging.exception(err)
        await call.answer("❗ Xatolik yuz berdi, iltimos qayta urinib ko'ring.")
