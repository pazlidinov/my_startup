from loader import dp
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart
from keyboards.inline.langsKeyboard import langs
from keyboards.default.contact import contact_btn
from states.clientData import Client
import logging


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
        "Pastki tugma orqali telefon raqamingizni kiriting\n⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️", reply_markup=contact_btn
    )
    await Client.phone_number.set()
    

@dp.callback_query_handler(state=Client.phone_number)
async def contact_stage(call: types.CallbackQuery, state: FSMContext):
    pass