from datetime import date
import logging
import os
from pathlib import Path

from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardButton, FSInputFile

from keyboards.inline import langsKeyboard, menu_client, monthsKeyboard
from utils.others.secret_code import generate_code
from utils.others.qr_code import generate_qr_code
from utils.db_api.database import all_tables as db

router = Router()

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


@router.callback_query(F.data == "client_new_qrcode")
async def new_qr_code_for_client(call: CallbackQuery):
    try:
        client = await db.select_client(telegram_id=str(call.from_user.id))
        path_img = client["qr_code"]
        #  safe delete
        if path_img and os.path.exists(path_img):
            os.remove(path_img)
        secret_code = await generate_code(10)
        qr_code = generate_qr_code(call.from_user.id, secret_code)
        await db.update_client(
            telegram_id=str(call.from_user.id), secret_code=secret_code, qr_code=qr_code
        )
        await call.message.delete()
        await call.answer(
            "✅ Tabriklaymiz, QrCode muvaffaqiyatli yangilandi", show_alert=True
        )
        await call.message.answer_photo(
            photo=FSInputFile(qr_code),
            caption="⬆️ QrCodeni reseptionga ko'rsating\n⬇️ Zalning QrCodeni skanerlang",
            reply_markup=menu_client.client_main_menu,
        )
    except Exception as err:
        logging.exception(err)
        await call.answer("❗ Xatolik yuz berdi, iltimos qayta urinib ko'ring.")


@router.callback_query(F.data.startswith("client_balance"))
async def client_balance_by_month(call: CallbackQuery):
    await call.answer()   
    try:
        if "month" in call.data:
            data_date = call.data.split("_")[-1]
            year = int(data_date.split("-")[0])
            month = int(data_date.split("-")[1])
            client_balance = await db.select_payment_by_month(
                telegram_id=str(call.from_user.id), year=year, month=month
            )
        else:
            today = date.today()
            year = int(today.year)
            month = int(today.month)
            client_balance = await db.select_payment_for_balance(
                telegram_id=str(call.from_user.id)
            )
    except Exception as err:
        logging.exception(err)
        return await call.answer("❗ Xatolik yuz berdi, iltimos qayta urinib ko'ring.")
    await call.message.delete()
    if not client_balance:
        send_text = f"🚫 {year}-yil {all_months[month-1]} oyida to'lovlar topilmadi"
    else:
        send_text = f"{year}-yil {all_months[month-1]} oyidagi to'lovlar:\n"
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


@router.callback_query(F.data.startswith("client_statistics"))
async def client_statistics(call: CallbackQuery):
    await call.answer()
    if "month" in call.data:
        data_date = call.data.split("_")[-1]
        year = int(data_date.split("-")[0])
        month = int(data_date.split("-")[1])
    else:
        today = date.today()
        year = int(today.year)
        month = int(today.month)
    try:
        client_statistics = await db.select_registrations_for_client(
            telegram_id=str(call.from_user.id), year=year, month=month
        )
    except Exception as err:
        logging.exception(err)
        return await call.answer("❗ Xatolik yuz berdi, iltimos qayta urinib ko'ring.")
    await call.message.delete()
    if not client_statistics:
        return await call.message.answer(
            text=f"🚫 {year}-yil {all_months[month-1]} oyida foallik topilmadi",
            reply_markup=monthsKeyboard.get_months_key("client", "statistics"),
        )
    send_text = f"{year}-yil {all_months[month-1]} oyidagi faollik:\n"
    for i, item in enumerate(client_statistics, start=1):
        send_text += (
            f"<b>{i}) <a href='https://maps.google.com/?"
            + f"q={item['loc_lat']},{item['loc_long']}'>"
            + f"{item['gym_name']}</a></b>\n"
            + f"<b>🗓️ Sana:</b> {item['date'].strftime('%Y-%m-%d %H:%M:%S')}\n"
            + f"<b>💵 To'lov:</b> {item['date_start']} kungi to'lov asosida\n"
        )
    return await call.message.answer(
        text=send_text,
        parse_mode="HTML",
        disable_web_page_preview=True,
        reply_markup=monthsKeyboard.get_months_key("client", "statistics"),
    )


@router.callback_query(F.data == "client_change_lang")
async def choose_client_lang(call: CallbackQuery):
    await call.answer()
    await call.message.delete()
    await call.message.answer(
        "🇺🇿Hurmatli mijoz, kerakli tilni tanlang!\n"
        "🇺🇿Ҳурматли мижоз, керакли тилни танланг!\n"
        "🇷🇺Уважаемый клиент, пожалуйста, выберите нужный язык!",
        reply_markup=langsKeyboard.langs(role="client", with_back_menu=True),
    )


@router.callback_query(F.data.startswith("client_lang"))
async def change_client_lang(call: CallbackQuery):    
    try:
        await db.update_client(
            telegram_id=str(call.from_user.id), language=call.data.split("_")[-1]
        )
        await call.message.delete()
        await call.answer(
            "✅ Tabriklaymiz, til muvaffaqiyatli yangilandi", show_alert=True
        )
        await call.message.answer_photo(
            photo=FSInputFile(MEDIA_DIR / f"{call.from_user.id}.png"),
            caption="⬆️ QrCodeni reseptionga ko'rsating\n⬇️ Zalning QrCodeni skanerlang",
            reply_markup=menu_client.client_main_menu,
        )
    except Exception as err:
        logging.exception(err)
        await call.answer("❗ Xatolik yuz berdi, iltimos qayta urinib ko'ring.")
