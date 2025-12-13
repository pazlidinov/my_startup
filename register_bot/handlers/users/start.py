from loader import dp, client_db
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart
from keyboards.inline.langsKeyboard import langs
from keyboards.default.contact import contact_btn
from states.clientData import Client
import logging

# import asyncio


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    await message.answer(
        "🇺🇿Hurmatli mijoz, kerakli tilni tanlang!\n"
        "🇺🇿Ҳурматли мижоз, керакли тилни танланг!\n"
        "🇷🇺Уважаемый клиент, пожалуйста, выберите нужный язык!",
        reply_markup=langs,
    )
    await Client.lang.set()


@dp.callback_query_handler(state=Client.lang)
async def lang_stage(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(user_name=call.from_user.username)
    await state.update_data(first_name=call.from_user.first_name)
    await state.update_data(last_name=call.from_user.last_name)
    await state.update_data(telegram_id=call.from_user.id)
    await state.update_data(language=call.data)

    await call.message.delete()
    await call.message.answer(
        "Pastki tugma orqali telefon raqamingizni kiriting\n⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️",
        reply_markup=contact_btn,
    )
    await Client.phone_number.set()


# @dp.message_handler(
#     content_types="contact", is_sender_contact=True, state=Client.phone_number
# )
@dp.message_handler(
    content_types=[types.ContentType.CONTACT],
    is_sender_contact=True,
    state=Client.phone_number,
)
async def contact_stage(message: types.Message, state: FSMContext):
    phonenumber = message.contact
    await state.update_data({"phone_number": phonenumber.phone_number})

    # Ma'limotlarni qayta o'qish
    data = await state.get_data()
    user_name = data.get("user_name")
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    telegram_id = data.get("telegram_id")
    phone_number = data.get("phone_number")
    language = data.get("language")
    secret_code = "123"
    qr_code = "///"

    try:
        await client_db.add_client(
            user_name=user_name,
            first_name=first_name,
            last_name=last_name,
            telegram_id=str(telegram_id),
            phone_number=phone_number,
            language=language,
            secret_code=secret_code,
            qr_code=qr_code,
        )
        await message.answer(
            "Tabriklaymiz, muvaffaqiyatli ro'yxatdan o'tdingiz",
            reply_markup=types.ReplyKeyboardRemove(),
        )

    except Exception as err:
        logging.exception(err)

    await state.finish()
    return
