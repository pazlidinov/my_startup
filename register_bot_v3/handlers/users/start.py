from datetime import datetime, timedelta
import logging
import asyncio
from pathlib import Path

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile, ReplyKeyboardRemove
from aiogram.filters import CommandStart, StateFilter, Command
from aiogram.fsm.context import FSMContext

from keyboards.inline import langsKeyboard, roleKeyboard, menu_client, menu_gym
from keyboards.default import contact, location
from states.clientData import Client
from utils.others.secret_code import generate_code
from utils.others.qr_code import generate_qr_code
from utils.db_api.database import all_tables as db

router = Router()


BASE_DIR = Path(__file__).resolve().parent.parent.parent
MEDIA_DIR = BASE_DIR / "qr_code_img"
MEDIA_DIR.mkdir(parents=True, exist_ok=True)


@router.message(CommandStart())
@router.message(Command("menu"))
async def bot_start(message: Message, state: FSMContext):
    await message.delete() 
    try:
        user_data = await db.check_user(telegram_id=str(message.from_user.id))
        if user_data is None:
            # user yo‘q
            user = {}
        else:
            user = dict(user_data)
        if not user:
            last_msg = await message.answer(
                "❗ Siz ro'yhatdan o'tmagansiz.\n📋 Iltimos, ro'yhatdan o'ting!"
            )
            await state.update_data(last_msg_id=last_msg.message_id)
            await message.answer(
                "🇺🇿Hurmatli mijoz, kerakli tilni tanlang!\n"
                "🇺🇿Ҳурматли мижоз, керакли тилни танланг!\n"
                "🇷🇺Уважаемый клиент, пожалуйста, выберите нужный язык!",
                reply_markup=langsKeyboard.langs("None"),
            )
            await state.set_state(Client.lang)
            return
        if not user["is_active"]:
            await message.answer(
                 text="❗ Siz aktiv holatda emassiz.\n"
                + "Agar 👷 hodim bo'lsangiz, 🧑‍💻 reseptionga murojaat qiling!\n"
                + "Agar 👥 mijoz bo'lsangiz, 🙋‍♂️ adminga murojaat qiling!"
            )
            return
        if user["source"] == "client":
            await message.answer_photo(
                photo=FSInputFile(user["qr_code"]),
                caption="⬆️ QrCodeni reseptionga ko'rsating\n⬇️ Zalning QrCodeni skanerlang",
                reply_markup=menu_client.client_main_menu,
            )
            return
        if user["source"] == "gym":
            await db.update_gym_by_worker(
                telegram_id=str(message.from_user.id),
                waiting_lump_sum=False,
                waiting_location=False,
            )
            await message.answer_photo(
                photo=FSInputFile(MEDIA_DIR / f"{message.from_user.id}.png"),
                caption="⬆️ QrCodeni mijozga ko'rsating\n⬇️ Mijozning QrCodeni skanerlang",
                reply_markup=menu_gym.gym_main_menu,
            )
            return
        else:
            return await message.answer(
                "❗ Xatolik yuz berdi, iltimos qayta urinib ko'ring."
            )
    except Exception as err:
        logging.exception(err)
        await message.answer("❗ Xatolik yuz berdi, iltimos qayta urinib ko'ring.")


@router.callback_query(Client.lang)
async def lang_stage(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.update_data(
        user_name=call.from_user.username,
        first_name=call.from_user.first_name,
        last_name=call.from_user.last_name,
        telegram_id=call.from_user.id,
        language=call.data.split("_")[-1],
    )
    data = await state.get_data()
    last_msg_id = data.get("last_msg_id")
    await call.bot.delete_message(chat_id=call.from_user.id, message_id=last_msg_id)

    # INLINE keyboardni olib tashlaymiz (MUHIM)
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.delete()

    last_msg = await call.message.answer(
        "Pastki tugma orqali telefon raqamingizni kiriting\n⏬⏬⏬⏬⏬⏬⏬⏬⏬⏬⏬⏬⏬⏬",
        reply_markup=contact.contact_btn,
    )
    await state.update_data(last_msg_id=last_msg.message_id)
    await state.set_state(Client.phone_number)


@router.message(StateFilter(Client.phone_number), F.contact)
async def contact_stage(message: Message, state: FSMContext):
    phonenumber = message.contact
    await state.update_data({"phone_number": phonenumber.phone_number})
    await message.delete()

    data = await state.get_data()
    last_msg_id = data.get("last_msg_id")
    await message.bot.delete_message(chat_id=message.chat.id, message_id=last_msg_id)

    await message.answer(
        "Botdan foydalanish turini tanlang...",
        reply_markup=roleKeyboard.roles,
    )
    await state.set_state(Client.role)


@router.callback_query(Client.role, F.data == "client")
async def for_client(call: CallbackQuery, state: FSMContext):
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
        await call.answer("✅ Tabriklaymiz, muvaffaqiyatli ro'yxatdan o'tdingiz")
        await call.message.answer_photo(
            photo=FSInputFile(qr_code),
            caption="⬆️ QrCodeni reseptionga ko'rsating\n⬇️ Zalning QrCodeni skanerlang",
            reply_markup=menu_client.client_main_menu,
        )
    except Exception as err:
        logging.exception(err)
        await call.message.answer("❗ Xatolik yuz berdi, iltimos qayta urinib ko'ring.")

    await state.clear()


@router.callback_query(Client.role, F.data == "worker")
async def for_worker(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    last_msg = await call.message.answer("Ro'yhatdan o'tish amalga oshirilmoqda...")

    # Ma'limotlarni qayta o'qish
    data = await state.get_data()

    # Yangi hodim DB ga qo'shish
    try:
        await db.add_worker(
            gym=None,
            user_name=data.get("user_name"),
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            telegram_id=str(data.get("telegram_id")),
            phone_number=data.get("phone_number"),
            language=data.get("language"),
            is_active=False,
        )
        await call.bot.delete_message(
            chat_id=call.message.chat.id, message_id=last_msg.message_id
        )
        await call.answer("✅ Tabriklaymiz, muvaffaqiyatli ro'yxatdan o'tdingiz", show_alert=True)
        qr_code = generate_qr_code(data.get("telegram_id"), data.get("telegram_id"))
        await call.message.answer_photo(
            photo=FSInputFile(qr_code),
            caption="⬆️ QrCodeni reseptionga ko'rsating\n",
        )
    except Exception as err:
        logging.exception(err)
        await call.bot.delete_message(
            chat_id=call.message.chat.id, message_id=last_msg.message_id
        )
        await call.message.answer("❗ Xatolik yuz berdi, iltimos qayta urinib ko'ring.")
    await state.clear()


@router.callback_query(Client.role, F.data == "director")
async def name_stage(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    last_msg = await call.message.answer("Sport zalingizning nomini kiriting...")
    await state.update_data(last_msg_id=last_msg.message_id)
    await state.set_state(Client.name)


@router.message(Client.name)
async def name_stage(message: Message, state: FSMContext):
    data = await state.get_data()
    last_msg_id = data.get("last_msg_id")
    await message.bot.delete_message(chat_id=message.chat.id, message_id=last_msg_id)

    await state.update_data(gym_name=message.text)
    await message.delete()

    last_msg = await message.answer(
        "Iltimos, joylashuvingizni yuboring\n⏬⏬⏬⏬⏬⏬⏬⏬⏬⏬⏬⏬⏬⏬",
        reply_markup=location.location_btn,
    )
    await state.update_data(last_msg_id=last_msg.message_id)
    await state.set_state(Client.location)


@router.message(Client.location, F.location)
async def get_location(message: Message, state: FSMContext):
    data = await state.get_data()
    last_msg_id = data.get("last_msg_id")
    await message.bot.delete_message(chat_id=message.chat.id, message_id=last_msg_id)
    await message.delete()

    lat = message.location.latitude
    lon = message.location.longitude
    await state.update_data({"loc_lat": lat})
    await state.update_data({"loc_long": lon})

    last_msg = await message.answer("Iltimos, bir kunlik to'lov miqdorini kiriting...")
    await state.update_data(last_msg_id=last_msg.message_id)

    await state.set_state(Client.lump_sum)


@router.message(Client.lump_sum)
async def lump_sum(message: Message, state: FSMContext):
    text = message.text.strip()

    data = await state.get_data()
    last_msg_id = data.get("last_msg_id")
    await message.bot.delete_message(chat_id=message.chat.id, message_id=last_msg_id)
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
            "✅ Tabriklaymiz, muvaffaqiyatli ro'yxatdan o'tdingiz."
        )
    except Exception as err:
        logging.exception(err)
        last_msg = await message.answer(
            "❗ Xatolik yuz berdi, iltimos qayta urinib ko'ring."
        )
    await asyncio.sleep(10)
    await message.bot.delete_message(
        chat_id=message.chat.id, message_id=last_msg.message_id
    )
    await message.answer_photo(
        photo=FSInputFile(qr_code),
        caption="⬆️ QrCodeni mijozga ko'rsating\n⬇️ Mijozning QrCodeni skanerlang",
        reply_markup=menu_gym.gym_main_menu,
    )
    await state.clear()
