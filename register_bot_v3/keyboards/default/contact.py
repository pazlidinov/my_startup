from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

contact_btn = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📞 Telefon raqamni yuborish", request_contact=True),
        ],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)
