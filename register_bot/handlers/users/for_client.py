from datetime import datetime, timedelta, date
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
from states.client_states import ClientLang
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent.parent
MEDIA_DIR = BASE_DIR / "qr_code_img"
MEDIA_DIR.mkdir(parents=True, exist_ok=True)


@dp.callback_query_handler(lambda c: c.data == "client_new_qrcode")
async def for_client(call: types.CallbackQuery):
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
        await call.answer(
            "❗ Xatolik yuz berdi, iltimos qayta urinib ko'ring.", show_alert=True
        )


@dp.callback_query_handler(lambda c: c.data == "client_balance")
async def choose_client_lang(call: types.CallbackQuery):
    await call.answer()
    try:
        client_balance = await db.select_payment_for_balance(
            telegram_id=str(call.from_user.id)
        )
    except Exception as err:
        logging.exception(err)
        return await call.answer(
            "❗ Xatolik yuz berdi, iltimos qayta urinib ko'ring.", show_alert=True
        )
    if client_balance == []:
        return await call.answer("🚫 Aktiv to'lovlar topilmadi", show_alert=True)
    send_message = ""
    for i, item in enumerate(client_balance[0], start=1):
    #     send_message += (
    #         f"{i}. <a href='https://maps.google.com/?q={item['loc_lat']},{item['loc_long']}'>{item['name']}</a>\n"
    #         + f"To'lov: {item['price']}\n"
    #         + f"Foydalanilgan: {item['count']}/{item['balanse']}\n"
    #         + f"Muddati: {item['date_start']}-{item['date_end']}"
    #         + f"Faolligi: {'Foal' if item['is_active'] else 'Foal emas'}\n"
    #     )
    # await call.message.answer(text=send_message)


@dp.callback_query_handler(lambda c: c.data == "client_statistics")
async def choose_client_lang(call: types.CallbackQuery):
    pass


@dp.callback_query_handler(lambda c: c.data == "client_lang")
async def choose_client_lang(call: types.CallbackQuery):
    await call.message.delete()
    await call.message.answer(
        "🇺🇿Hurmatli mijoz, kerakli tilni tanlang!\n"
        "🇺🇿Ҳурматли мижоз, керакли тилни танланг!\n"
        "🇷🇺Уважаемый клиент, пожалуйста, выберите нужный язык!",
        reply_markup=langsKeyboard.langs,
    )
    await ClientLang.lang.set()


@dp.callback_query_handler(state=ClientLang.lang)
async def change_client_lang(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    try:
        await db.update_client(telegram_id=str(call.from_user.id), language=call.data)
        await call.message.delete()
        await call.answer(
            "☑️ Tabriklaymiz, til muvaffaqiyatli yangilandi", show_alert=True
        )
        await call.message.answer_photo(
            open(MEDIA_DIR / f"{call.from_user.id}.png", "rb"),
            caption="⬆️ QrCodeni reseptionga ko'rsating\n⬇️ Zalning QrCodeni skanerlang",
            reply_markup=menu_client.client_main_menu,
        )
    except Exception as err:
        logging.exception(err)
        await call.answer(
            "❗ Xatolik yuz berdi, iltimos qayta urinib ko'ring.", show_alert=True
        )
    await state.finish()


# [<Record
#  id=3
#  balanse=10
#  price=10
#  is_trainer=True
#  is_active=True
#  client_id=46
#  gym_id=5
#  count=5
#  date_end=datetime.date(2026, 1, 20)
#  date_start=datetime.date(2026, 1, 16)
#  id=5 name='Power' loc_lat=40.709368 loc_long=72.283077 secret_code='UDiA4f9ouo' qr_code='C:\\Users\\User\\Documents\\GitHub\\my_startup\\register_bot\\qr_code_img\\141253372.png' is_active=True date_end=datetime.date(2026, 2, 9) lump_sum=6363 balance=0
#  id=46 first_name='Zoxidaxon' last_name='Pazlidinova💎' telegram_id='8294197772' phone_number='998999213380' secret_code='ROAyDPLRYH' qr_code='C:\\Users\\User\\Documents\\GitHub\\my_startup\\register_bot\\qr_code_img\\8294197772.png' is_active=True language='lotin' user_name='zoxida_2728'
#  >]
