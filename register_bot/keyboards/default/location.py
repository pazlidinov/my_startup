from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

location_btn = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📍 Joylashuvni yuborish", request_location=True),
        ],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)
