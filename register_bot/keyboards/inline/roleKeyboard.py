from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

roles=InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="", callback_data='director'),],
        [InlineKeyboardButton(text="🇺🇿 Кирилча", callback_data='worker'),],
        [InlineKeyboardButton(text="🇷🇺 Русский язык", callback_data='client'),],
    ]
)