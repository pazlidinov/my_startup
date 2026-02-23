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
from aiogram.types import InlineKeyboardButton, ReplyKeyboardRemove
from keyboards.default import contact, location

BASE_DIR = Path(__file__).resolve().parent.parent.parent
MEDIA_DIR = BASE_DIR / "qr_code_img"
MEDIA_DIR.mkdir(parents=True, exist_ok=True)


@dp.callback_query_handler(lambda c: c.data == "gym_change_lump_sum")
async def wait_Lum_sum(call: types.CallbackQuery):
    await call.answer()
    try:
        is_director = dict(await db.select_worker(telegram_id=str(call.from_user.id)))[
            "is_director"
        ]
    except Exception as err:
        logging.exception(err)
        await call.message.answer("❗ Xatolik yuz berdi, iltimos qayta urinib ko'ring.")
    if is_director:
        try:
            await db.update_gym_by_worker(
                telegram_id=str(call.from_user.id),
                waiting_lump_sum=True,
            )
            await call.message.answer(
                text="🔙 Sozlamalarga qaytish",
                reply_markup=menu_gym.gym_back_settings,
            )
            await call.message.answer(
                "Iltimos, bir kunlik to'lov miqdorini kiriting..."
            )
        except Exception as err:
            logging.exception(err)
            await call.message.answer(
                "❗ Xatolik yuz berdi, iltimos qayta urinib ko'ring."
            )
    else:
        await call.message.answer(
            "❗ Siz zal egasi bo'lmaganligiz uchun joylashuvni o'zgartirolmaysiz."
        )


@dp.message_handler(lambda message: True, state=None)
async def change_lump_sum(message: types.Message):
    print("ok")
    text = message.text.strip()
    # ❌ Agar int bo‘lmasa, qayta so‘rash
    if not text.isdigit():
        await message.answer("❌ Iltimos, faqat **butun son** kiriting!")
        await message.delete()
        return

    try:
        is_director = dict(
            await db.select_worker(telegram_id=str(message.from_user.id))
        )["is_director"]
        waiting_lump_sum = dict(
            await db.select_gym_by_worker(telegram_id=str(message.from_user.id))
        )["waiting_lump_sum"]
    except Exception as err:
        logging.exception(err)
        await message.answer("❗ Xatolik yuz berdi, iltimos qayta urinib ko'ring.")

    # if not waiting_lump_sum:
    #     await echo.bot_echo(message)
    #     return
    # ✅ Raqamni int ga aylantiramiz
    amount = int(text)
    # Optional: minimal / maksimal cheklov
    MIN_AMOUNT = 1
    MAX_AMOUNT = 2147483647
    if amount < MIN_AMOUNT or amount > MAX_AMOUNT:
        await message.answer(
            f"❌ Miqdor {MIN_AMOUNT}-{MAX_AMOUNT} oralig‘ida bo‘lishi kerak!"
        )
        await message.delete()
        return
    if not is_director:
        await message.answer(
            "❗ Siz zal egasi bo'lmaganligiz uchun bir kunlik to'lovni o'zgartirolmaysiz."
        )
    if is_director and waiting_lump_sum:
        try:
            await db.update_gym_by_worker(
                telegram_id=str(message.from_user.id),
                lump_sum=amount,
                waiting_lump_sum=False,
            )
            await message.answer(
                "☑️ Tabriklaymiz, joylabir kunlik to'lov muvaffaqiyatli yangilandi.",
            )
            await message.answer(
                text="⚙️ Sozlamalar",
                reply_markup=menu_gym.gym_settings_menu,
            )
        except Exception as err:
            logging.exception(err)
            await message.answer("❗ Xatolik yuz berdi, iltimos qayta urinib ko'ring.")
    else:
        await message.answer("❗ Xatolik yuz berdi, iltimos qayta urinib ko'ring.")


@dp.callback_query_handler(lambda c: c.data == "gym_change_location")
async def wait_location(call: types.CallbackQuery):
    await call.answer()
    try:
        is_director = dict(await db.select_worker(telegram_id=str(call.from_user.id)))[
            "is_director"
        ]
    except Exception as err:
        logging.exception(err)
        await call.message.answer("❗ Xatolik yuz berdi, iltimos qayta urinib ko'ring.")
    if is_director:
        try:
            await db.update_gym_by_worker(
                telegram_id=str(call.from_user.id),
                waiting_location=True,
            )
            await call.message.answer(
                text="🔙 Sozlamalarga qaytish",
                reply_markup=menu_gym.gym_back_settings,
            )
            await call.message.answer(
                "Iltimos, joylashuvingizni yuboring\n⏬⏬⏬⏬⏬⏬⏬⏬⏬⏬⏬⏬⏬⏬",
                reply_markup=location.location_btn,
            )
        except Exception as err:
            logging.exception(err)
            await call.message.answer(
                "❗ Xatolik yuz berdi, iltimos qayta urinib ko'ring."
            )
    else:
        await call.message.answer(
            "❗ Siz zal egasi bo'lmaganligiz uchun joylashuvni o'zgartirolmaysiz."
        )


@dp.message_handler(content_types=["location"])
async def change_location(message: types.Message):
    await message.delete()
    try:
        is_director = dict(
            await db.select_worker(telegram_id=str(message.from_user.id))
        )["is_director"]
        waiting_location = dict(
            await db.select_gym_by_worker(telegram_id=str(message.from_user.id))
        )["waiting_location"]
    except Exception as err:
        logging.exception(err)
        await message.answer("❗ Xatolik yuz berdi, iltimos qayta urinib ko'ring.")

    if is_director and waiting_location:
        try:
            await db.update_gym_by_worker(
                telegram_id=str(message.from_user.id),
                loc_lat=message.location.latitude,
                loc_long=message.location.longitude,
                waiting_location=False,
            )
            await message.answer(
                "☑️ Tabriklaymiz, joylashuv muvaffaqiyatli yangilandi.",
                reply_markup=ReplyKeyboardRemove(),
            )
            await message.answer(
                text="⚙️ Sozlamalar",
                reply_markup=menu_gym.gym_settings_menu,
            )
        except Exception as err:
            logging.exception(err)
            await message.answer("❗ Xatolik yuz berdi, iltimos qayta urinib ko'ring.")
    else:
        await message.answer(
            "❗ Siz zal egasi bo'lmaganligiz uchun joylashuvni o'zgartirolmaysiz."
        )


@dp.callback_query_handler(lambda c: c.data == "gym_new_qrcode")
async def new_qr_code_for_gym(call: types.CallbackQuery):
    await call.answer()
    try:
        is_director = dict(await db.select_worker(telegram_id=str(call.from_user.id)))[
            "is_director"
        ]
    except Exception as err:
        logging.exception(err)
        await call.message.answer("❗ Xatolik yuz berdi, iltimos qayta urinib ko'ring.")
    if is_director:
        try:
            secret_code = await generate_code(10)
            qr_code = generate_qr_code(call.from_user.id, secret_code)
            await db.update_gym_by_worker(
                telegram_id=str(call.from_user.id),
                secret_code=secret_code,
                qr_code=qr_code,
            )
            all_worker = await db.sort_worker_by_gym(telegram_id=str(call.from_user.id))
            for item in all_worker:
                if item["telegram_id"] == str(call.from_user.id):
                    continue
                os.remove(MEDIA_DIR / f"{item['telegram_id']}.png")
                qr_code = generate_qr_code(item["telegram_id"], secret_code)

            await call.message.delete()
            await call.message.answer(
                "☑️ Tabriklaymiz, QrCode muvaffaqiyatli yangilandi."
            )
            return await call.message.answer_photo(
                open(MEDIA_DIR / f"{call.from_user.id}.png", "rb"),
                caption="⬆️ QrCodeni mijozga ko'rsating\n⬇️ Mijozning QrCodeni skanerlang",
                reply_markup=menu_gym.gym_main_menu,
            )
        except Exception as err:
            logging.exception(err)
            await call.message.answer(
                "❗ Xatolik yuz berdi, iltimos qayta urinib ko'ring."
            )
    else:
        await call.message.answer(
            "❗ Siz zal egasi bo'lmaganligiz uchun QRcodeni o'zgartirolmaysiz."
        )


@dp.callback_query_handler(lambda c: c.data == "gym_change_lang")
async def choose_gym_lang(call: types.CallbackQuery):
    await call.answer()
    await call.message.delete()
    langs_for_client = langsKeyboard.langs("gym")
    await call.message.answer(
        "🇺🇿Hurmatli mijoz, kerakli tilni tanlang!\n"
        "🇺🇿Ҳурматли мижоз, керакли тилни танланг!\n"
        "🇷🇺Уважаемый клиент, пожалуйста, выберите нужный язык!",
        reply_markup=langs_for_client.add(
            InlineKeyboardButton(text="⚙️ Sozlamalar", callback_data="gym_settings")
        ),
    )


@dp.callback_query_handler(lambda c: c.data.startswith("gym_lang"))
async def change_gym_lang(call: types.CallbackQuery):
    await call.answer()
    try:
        await db.update_worker(
            telegram_id=str(call.from_user.id), language=call.data.split("_")[-1]
        )
        await call.message.delete()
        await call.answer("☑️ Tabriklaymiz, til muvaffaqiyatli yangilandi")
        await call.message.answer(
            text="⚙️ Sozlamalar", reply_markup=menu_gym.gym_settings_menu
        )
    except Exception as err:
        logging.exception(err)
        await call.answer("❗ Xatolik yuz berdi, iltimos qayta urinib ko'ring.")
