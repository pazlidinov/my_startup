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
    print(call.data)
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
