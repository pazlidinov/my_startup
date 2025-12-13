from loader import bot, dp, client_db
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart
from keyboards.inline.langsKeyboard import langs
from keyboards.inline.roleKeyboard import roles
from keyboards.default.contact import contact_btn
from states.clientData import Client
import logging


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    await message.delete()
    await message.answer(
        "🇺🇿Hurmatli mijoz, kerakli tilni tanlang!\n"
        "🇺🇿Ҳурматли мижоз, керакли тилни танланг!\n"
        "🇷🇺Уважаемый клиент, пожалуйста, выберите нужный язык!",
        reply_markup=langs,
    )
    await Client.lang.set()


@dp.callback_query_handler(state=Client.lang)
async def lang_stage(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await state.update_data(
        user_name=call.from_user.username,
        first_name=call.from_user.first_name,
        last_name=call.from_user.last_name,
        telegram_id=call.from_user.id,
        language=call.data,
    )
    # INLINE keyboardni olib tashlaymiz (MUHIM)
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.delete()

    last_msg = await call.message.answer(
        "Pastki tugma orqali telefon raqamingizni kiriting\n⏬⏬⏬⏬⏬⏬⏬⏬⏬⏬⏬⏬⏬⏬",
        reply_markup=contact_btn,
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
        reply_markup=roles,
    )
    await Client.role.set()


@dp.callback_query_handler(state=Client.role)
async def lang_stage(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()

    role = call.data
    print(type(role))
    if role == "director":
        await call.message.answer("director")
    elif role == "worker":
        await call.message.answer("worker")
    elif role == "client":
        await call.message.answer("client")
    else:
        await call.message.answer("NO")

    # # Ma'limotlarni qayta o'qish
    # data = await state.get_data()
    # user_name = data.get("user_name")
    # first_name = data.get("first_name")
    # last_name = data.get("last_name")
    # telegram_id = data.get("telegram_id")
    # phone_number = data.get("phone_number")
    # language = data.get("language")
    # secret_code = "123"
    # qr_code = "///"

    # try:
    #     await client_db.add_client(
    #         user_name=user_name,
    #         first_name=first_name,
    #         last_name=last_name,
    #         telegram_id=str(telegram_id),
    #         phone_number=phone_number,
    #         language=language,
    #         secret_code=secret_code,
    #         qr_code=qr_code,
    #     )
    #     await message.answer(
    #         "Tabriklaymiz, muvaffaqiyatli ro'yxatdan o'tdingiz",
    #         reply_markup=types.ReplyKeyboardRemove(),
    #     )

    # except Exception as err:
    #     logging.exception(err)

    # await state.finish()
    # return
