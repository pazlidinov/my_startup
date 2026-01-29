from datetime import datetime, timedelta
from loader import bot, dp
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart
from keyboards.inline import langsKeyboard, roleKeyboard, menu_client, menu_gym
from keyboards.default import contact, location
from states.clientData import Client
from utils.others.secret_code import generate_code
from utils.others.qr_code import generate_qr_code
from utils.db_api.database import all_tables as db
import logging
import asyncio
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
MEDIA_DIR = BASE_DIR / "qr_code_img"
MEDIA_DIR.mkdir(parents=True, exist_ok=True)


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    await message.delete()
    try:
        user = dict(await db.check_user(telegram_id=str(message.from_user.id)))
        if not user:
            await message.answer(
                "❗ Siz ro'yhatdan o'tmagansiz.\n📋 Iltimos, ro'yhatdan o'ting!"
            )
            await message.answer(
                "🇺🇿Hurmatli mijoz, kerakli tilni tanlang!\n"
                "🇺🇿Ҳурматли мижоз, керакли тилни танланг!\n"
                "🇷🇺Уважаемый клиент, пожалуйста, выберите нужный язык!",
                reply_markup=langsKeyboard.langs("None"),
            )
        if not user["is_active"]:
            await message.answer(
                text="❗ Siz aktiv holatda emassiz.\n"
                + "Agar 👨‍👦‍👦 hodim bo'lsangiz, reseptionga murojaat qiling!\n"
                + "Agar mijoz bo'lsangiz, admin murojaat qiling!"
            )
        if user["source"] == "client":
            await message.answer_photo(
                open(user["qr_code"], "rb"),
                caption="⬆️ QrCodeni reseptionga ko'rsating\n⬇️ Zalning QrCodeni skanerlang",
                reply_markup=menu_client.client_main_menu,
            )
        if user["source"] == "gym":
            await message.answer_photo(
                open(MEDIA_DIR / f"{message.from_user.id}.png", "rb"),
                caption="⬆️ QrCodeni reseptionga ko'rsating\n⬇️ Zalning QrCodeni skanerlang",
                reply_markup=menu_gym.gym_main_menu,
            )
    except Exception as err:
        logging.exception(err)
        await message.answer("❗ Xatolik yuz berdi, iltimos qayta urinib ko'ring.")


@dp.callback_query_handler(state=Client.lang)
async def lang_stage(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await state.update_data(
        user_name=call.from_user.username,
        first_name=call.from_user.first_name,
        last_name=call.from_user.last_name,
        telegram_id=call.from_user.id,
        language=call.data.split("_")[-1],
    )
    # INLINE keyboardni olib tashlaymiz (MUHIM)
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.delete()

    last_msg = await call.message.answer(
        "Pastki tugma orqali telefon raqamingizni kiriting\n⏬⏬⏬⏬⏬⏬⏬⏬⏬⏬⏬⏬⏬⏬",
        reply_markup=contact.contact_btn,
    )
    await state.update_data(last_msg_id=last_msg.message_id)
    await Client.phone_number.set()


@dp.message_handler(
    content_types=[types.ContentType.CONTACT],
    is_sender_contact=True,
    state=Client.phone_number,
)
async def contact_stage(message: types.Message, state: FSMContext):
    phonenumber = message.contact
    await state.update_data({"phone_number": phonenumber.phone_number})
    await message.delete()

    data = await state.get_data()
    last_msg_id = data.get("last_msg_id")
    await bot.delete_message(chat_id=message.chat.id, message_id=last_msg_id)

    await message.answer(
        "Botdan foydalanish turini tanlang...",
        reply_markup=roleKeyboard.roles,
    )
    await Client.role.set()


@dp.callback_query_handler(lambda c: c.data == "client", state=Client.role)
async def for_client(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()

    # Ma'limotlarni qayta o'qish
    data = await state.get_data()
    secret_code = await generate_code(10)
    qr_code = generate_qr_code(data.get("telegram_id"), secret_code)

    # Yangi foydalanuvchi DB ga qo'shish
    try:
        await db.add_client(
            user_name=data.get("user_name"),
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            telegram_id=str(data.get("telegram_id")),
            phone_number=data.get("phone_number"),
            language=data.get("language"),
            secret_code=secret_code,
            qr_code=qr_code,
        )
        await call.answer(
            "☑️ Tabriklaymiz, muvaffaqiyatli ro'yxatdan o'tdingiz", show_alert=True
        )
        await call.message.answer_photo(
            open(qr_code, "rb"),
            caption="⬆️ QrCodeni reseptionga ko'rsating\n⬇️ Zalning QrCodeni skanerlang",
            reply_markup=menu_client.client_main_menu,
        )
    except Exception as err:
        logging.exception(err)
        await call.message.answer(
            "❗ Xatolik yuz berdi, iltimos qayta urinib ko'ring.", show_alert=True
        )

    await state.finish()


@dp.callback_query_handler(lambda c: c.data == "worker", state=Client.role)
async def for_worker(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    last_msg = await call.message.answer("Ro'yhatdan o'tish amalga oshirilmoqda...")

    # Ma'limotlarni qayta o'qish
    data = await state.get_data()

    # Yangi hodim DB ga qo'shish
    try:
        await db.add_worker(
            user_name=data.get("user_name"),
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            telegram_id=str(data.get("telegram_id")),
            phone_number=data.get("phone_number"),
            language=data.get("language"),
            is_active=False,
        )
        await bot.delete_message(
            chat_id=call.message.chat.id, message_id=last_msg.message_id
        )
        await call.answer(
            "☑️ Tabriklaymiz, muvaffaqiyatli ro'yxatdan o'tdingiz", show_alert=True
        )
        qr_code = generate_qr_code(data.get("telegram_id"), data.get("telegram_id"))
        await call.message.answer_photo(
            open(qr_code, "rb"),
            caption="⬆️ QrCodeni reseptionga ko'rsating\n",
        )
    except Exception as err:
        logging.exception(err)
        await bot.delete_message(
            chat_id=call.message.chat.id, message_id=last_msg.message_id
        )
        await call.message.answer(
            "❗ Xatolik yuz berdi, iltimos qayta urinib ko'ring.", show_alert=True
        )
    await state.finish()


@dp.callback_query_handler(lambda c: c.data == "director", state=Client.role)
async def name_stage(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    last_msg = await call.message.answer("Sport zalingizning nomini kiriting...")
    await state.update_data(last_msg_id=last_msg.message_id)
    await Client.name.set()


@dp.message_handler(state=Client.name)
async def name_stage(message: types.Message, state: FSMContext):
    data = await state.get_data()
    last_msg_id = data.get("last_msg_id")
    await bot.delete_message(chat_id=message.chat.id, message_id=last_msg_id)

    await state.update_data(gym_name=message.text)
    await message.delete()

    last_msg = await message.answer(
        "Iltimos, joylashuvingizni yuboring\n⏬⏬⏬⏬⏬⏬⏬⏬⏬⏬⏬⏬⏬⏬",
        reply_markup=location.location_btn,
    )
    await state.update_data(last_msg_id=last_msg.message_id)
    await Client.location.set()


@dp.message_handler(content_types=["location"], state=Client.location)
async def get_location(message: types.Message, state: FSMContext):
    data = await state.get_data()
    last_msg_id = data.get("last_msg_id")
    await bot.delete_message(chat_id=message.chat.id, message_id=last_msg_id)
    await message.delete()

    lat = message.location.latitude
    lon = message.location.longitude
    await state.update_data({"loc_lat": lat})
    await state.update_data({"loc_long": lon})

    last_msg = await message.answer("Iltimos, bir kunlik to'lov miqdorini kiriting...")
    await state.update_data(last_msg_id=last_msg.message_id)

    await Client.lump_sum.set()


@dp.message_handler(state=Client.lump_sum)
async def lump_sum(message: types.Message, state: FSMContext):
    text = message.text.strip()

    data = await state.get_data()
    last_msg_id = data.get("last_msg_id")
    await bot.delete_message(chat_id=message.chat.id, message_id=last_msg_id)
    await message.delete()

    # ❌ Agar int bo‘lmasa, qayta so‘rash
    if not text.isdigit():
        await message.answer("❌ Iltimos, faqat **butun son** kiriting!")
        await message.delete()
        return

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

    secret_code = await generate_code(10)
    qr_code = generate_qr_code(data.get("telegram_id"), secret_code)
    free_day = await db.select_admin(column="free_days")
    today = datetime.today().date()
    after_free_days = today + timedelta(days=free_day)

    # Yangi hodim DB ga qo'shish
    try:
        new_gym_id = await db.add_gym(
            name=data.get("gym_name"),
            loc_lat=data.get("loc_lat"),
            loc_long=data.get("loc_long"),
            secret_code=secret_code,
            qr_code=qr_code,
            lump_sum=amount,
            date_end=after_free_days,
        )
        await db.add_worker(
            gym=new_gym_id,
            user_name=data.get("user_name"),
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            telegram_id=str(data.get("telegram_id")),
            phone_number=data.get("phone_number"),
            language=data.get("language"),
            is_director=True,
        )
        last_msg = await message.answer(
            "☑️ Tabriklaymiz, muvaffaqiyatli ro'yxatdan o'tdingiz."
        )
    except Exception as err:
        logging.exception(err)
        last_msg = await message.answer(
            "❗ Xatolik yuz berdi, iltimos qayta urinib ko'ring."
        )
    await asyncio.sleep(10)
    await bot.delete_message(chat_id=message.chat.id, message_id=last_msg.message_id)
    await message.answer_photo(
        open(qr_code, "rb"),
        caption="⬆️ QrCodeni mijozga ko'rsating\n⬇️ Mijozning QrCodeni skanerlang",
        reply_markup=menu_gym.gym_main_menu,
    )
    await state.finish()
