import logging
import os
import asyncio
from pathlib import Path

from aiogram import Router, F
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    ReplyKeyboardRemove,
    Message,
    FSInputFile,
)

from keyboards.inline import langsKeyboard, menu_gym, workerKeyboard
from keyboards.default import location
from utils.others.secret_code import generate_code
from utils.others.qr_code import generate_qr_code
from utils.db_api.database import all_tables as db

router = Router()

BASE_DIR = Path(__file__).resolve().parent.parent.parent
MEDIA_DIR = BASE_DIR / "qr_code_img"
MEDIA_DIR.mkdir(parents=True, exist_ok=True)


@router.callback_query(F.data == "gym_worker")
async def show_worker(call: CallbackQuery):
    await call.answer()
    try:
        all_worker = await db.sort_worker_by_gym(telegram_id=str(call.from_user.id))
    except Exception as err:
        logging.exception(err)
        await call.message.answer("❗ Xatolik yuz berdi, iltimos qayta urinib ko'ring.")
        return
    await call.message.delete()
    if all_worker == []:
        return await call.answer("🚫 Hodimlar topilmadi")
    worker_list = {}
    show_key = True
    send_text = "👥 Hodimlar:\n"
    for i, item in enumerate(all_worker, start=1):
        send_text += (
            f"<b>{i}) ✏️ Ismi:</b> <a href='tg://user?id={item['telegram_id']}'>"
            + f"{item['first_name']}</a>\n"
            + f"<b>📞 Telefon raqami:</b> +{item['phone_number']}\n"
            + f"<b>📋 Role:</b> {'🕵️ Director' if item['is_director'] else '🧍‍♂️ Hodim'}\n"
            + f"<b>⭕ Faolligi:</b> {'✅ Foal' if item['is_active'] else '❌ Foal emas'}\n"
        )
        if not item["is_director"]:
            worker_list[item["first_name"]] = item["telegram_id"]
            if item["telegram_id"] == call.from_user.id:
                show_key = False

    await call.message.answer(
        text=send_text,
        parse_mode="HTML",
        disable_web_page_preview=True,
        reply_markup=workerKeyboard.get_worker_key(
            show_key=show_key, worker_list=worker_list
        ),
    )


@router.callback_query(F.data.startswith("gym_woker_delete_"))
async def delete_worker(call: CallbackQuery):
    await call.answer()
    try:
        is_director = dict(await db.select_worker(telegram_id=str(call.from_user.id)))[
            "is_director"
        ]
    except Exception as err:
        logging.exception(err)
        await call.message.answer("❗ Xatolik yuz berdi, iltimos qayta urinib ko'ring.")
        return
    if is_director:
        try:
            worker = await db.select_worker(telegram_id=str(call.data.split("_")[-1]))
            os.remove(MEDIA_DIR / f"{worker['telegram_id']}.png")
            await db.update_worker(gym=None)
            qr_code = generate_qr_code(worker["telegram_id"], worker["telegram_id"])
        except Exception as err:
            logging.exception(err)
            await call.message.answer(
                "❗ Xatolik yuz berdi, iltimos qayta urinib ko'ring."
            )
        await call.message.delete()
    else:
        await call.message.answer(
            "❗ Siz zal egasi bo'lmaganligiz uchun hodimni o'chira olmaysiz."
        )


@router.callback_query(F.data == "gym_change_lump_sum")
async def wait_Lum_sum(call: CallbackQuery):
    await call.answer()
    try:
        is_director = dict(await db.select_worker(telegram_id=str(call.from_user.id)))[
            "is_director"
        ]
    except Exception as err:
        logging.exception(err)
        await call.message.answer("❗ Xatolik yuz berdi, iltimos qayta urinib ko'ring.")
        return
    if is_director:
        try:
            await db.update_gym_by_worker(
                telegram_id=str(call.from_user.id),
                waiting_lump_sum=True,
            )
            await call.message.delete()
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


@router.message(F.text)
async def change_lump_sum(message: Message):
    text = message.text.strip()
    # ❌ Agar int bo‘lmasa, qayta so‘rash
    if not text.isdigit():
        await message.answer("❌ Iltimos, faqat **butun son** kiriting!")
        await message.delete()
        return

    try:
        waiting_lump_sum = dict(
            await db.select_gym_by_worker(telegram_id=str(message.from_user.id))
        )["waiting_lump_sum"]
    except Exception as err:
        logging.exception(err)
        await message.answer("❗ Xatolik yuz berdi, iltimos qayta urinib ko'ring.")
        return

    if waiting_lump_sum:
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
        try:
            is_director = dict(
                await db.select_worker(telegram_id=str(message.from_user.id))
            )["is_director"]
        except Exception as err:
            logging.exception(err)
            await message.answer("❗ Xatolik yuz berdi, iltimos qayta urinib ko'ring.")
            return
        if not is_director:
            return await message.answer(
                "❗ Siz zal egasi bo'lmaganligiz uchun bir kunlik to'lovni o'zgartirolmaysiz."
            )

        if is_director:
            try:
                await db.update_gym_by_worker(
                    telegram_id=str(message.from_user.id),
                    lump_sum=amount,
                    waiting_lump_sum=False,
                )
                await message.delete()
                await message.answer(
                    "✅ Tabriklaymiz, joylabir kunlik to'lov muvaffaqiyatli yangilandi."
                )
                return await message.answer(
                    text="⚙️ Sozlamalar",
                    reply_markup=menu_gym.gym_settings_menu,
                )
            except Exception as err:
                logging.exception(err)
                return await message.answer(
                    "❗ Xatolik yuz berdi, iltimos qayta urinib ko'ring."
                )
        else:
            await message.answer("❗ Xatolik yuz berdi, iltimos qayta urinib ko'ring.")
            return


@router.callback_query(F.data == "gym_change_location")
async def wait_location(call: CallbackQuery):
    await call.answer()
    try:
        is_director = dict(await db.select_worker(telegram_id=str(call.from_user.id)))[
            "is_director"
        ]
    except Exception as err:
        logging.exception(err)
        await call.message.answer("❗ Xatolik yuz berdi, iltimos qayta urinib ko'ring.")
        return
    if is_director:
        try:
            await db.update_gym_by_worker(
                telegram_id=str(call.from_user.id),
                waiting_location=True,
            )
            await call.message.delete()
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


@router.message(F.location)
async def change_location(message: Message):
    await message.delete()
    try:
        waiting_location = dict(
            await db.select_gym_by_worker(telegram_id=str(message.from_user.id))
        )["waiting_location"]
    except Exception as err:
        logging.exception(err)
        await message.answer("❗ Xatolik yuz berdi, iltimos qayta urinib ko'ring.")
        return
    if waiting_location:
        try:
            is_director = dict(
                await db.select_worker(telegram_id=str(message.from_user.id))
            )["is_director"]
        except Exception as err:
            logging.exception(err)
            await message.answer("❗ Xatolik yuz berdi, iltimos qayta urinib ko'ring.")
            return
        if is_director:
            try:
                await db.update_gym_by_worker(
                    telegram_id=str(message.from_user.id),
                    loc_lat=message.location.latitude,
                    loc_long=message.location.longitude,
                    waiting_location=False,
                )
                await message.answer(
                    "✅ Tabriklaymiz, joylashuv muvaffaqiyatli yangilandi.",
                    reply_markup=ReplyKeyboardRemove(),
                )
                await message.answer(
                    text="⚙️ Sozlamalar",
                    reply_markup=menu_gym.gym_settings_menu,
                )
            except Exception as err:
                logging.exception(err)
                await message.answer(
                    "❗ Xatolik yuz berdi, iltimos qayta urinib ko'ring."
                )
                return
        else:
            await message.answer(
                "❗ Siz zal egasi bo'lmaganligiz uchun joylashuvni o'zgartirolmaysiz."
            )


@router.callback_query(F.data == "gym_new_qrcode")
async def new_qr_code_for_gym(call: CallbackQuery):
    await call.answer()
    try:
        is_director = dict(await db.select_worker(telegram_id=str(call.from_user.id)))[
            "is_director"
        ]
    except Exception as err:
        logging.exception(err)
        await call.message.answer("❗ Xatolik yuz berdi, iltimos qayta urinib ko'ring.")
        return
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
                    await call.message.delete()
                    await call.message.answer(
                        "✅ Tabriklaymiz, QrCode muvaffaqiyatli yangilandi."
                    )
                    await call.message.answer_photo(
                        photo=FSInputFile(MEDIA_DIR / f"{item['telegram_id']}.png"),
                        caption="⬆️ QrCodeni mijozga ko'rsating\n⬇️ Mijozning QrCodeni skanerlang",
                        reply_markup=menu_gym.gym_main_menu,
                    )
                    continue
                os.remove(MEDIA_DIR / f"{item['telegram_id']}.png")
                qr_code = generate_qr_code(item["telegram_id"], secret_code)
                await call.bot.send_message(
                    chat_id=item["telegram_id"],
                    text="⚠️ Sport zal QrCode yangilangandi!",
                )
                await call.message.answer_photo(
                    photo=FSInputFile(MEDIA_DIR / f"{item['telegram_id']}.png"),
                    caption="⬆️ QrCodeni mijozga ko'rsating\n⬇️ Mijozning QrCodeni skanerlang",
                    reply_markup=menu_gym.gym_main_menu,
                )
                await asyncio.sleep(0.05)
        except Exception as err:
            logging.exception(err)
            await call.message.answer(
                "❗ Xatolik yuz berdi, iltimos qayta urinib ko'ring."
            )
            return
    else:
        await call.message.answer(
            "❗ Siz zal egasi bo'lmaganligiz uchun QRcodeni o'zgartirolmaysiz."
        )


@router.callback_query(F.data == "gym_change_lang")
async def choose_gym_lang(call: CallbackQuery):
    await call.answer()
    await call.message.delete()
    await call.message.answer(
        "🇺🇿Hurmatli mijoz, kerakli tilni tanlang!\n"
        "🇺🇿Ҳурматли мижоз, керакли тилни танланг!\n"
        "🇷🇺Уважаемый клиент, пожалуйста, выберите нужный язык!",
        reply_markup=langsKeyboard.langs(
            role="gym", with_back_menu=True, with_back_settins=True
        ),
    )


@router.callback_query(F.data.startswith("gym_lang"))
async def change_gym_lang(call: CallbackQuery):  
    await call.answer()
    await call.message.delete()
    try:
        await db.update_worker(
            telegram_id=str(call.from_user.id), language=call.data.split("_")[-1]
        )
        await call.answer("✅ Tabriklaymiz, til muvaffaqiyatli yangilandi", show_alert=True)
        await call.message.answer(
            text="⚙️ Sozlamalar", reply_markup=menu_gym.gym_settings_menu
        )
    except Exception as err:
        logging.exception(err)
        await call.answer("❗ Xatolik yuz berdi, iltimos qayta urinib ko'ring.")
