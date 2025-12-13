from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

langs=InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🇺🇿 O'zbek tilida", callback_data='lotin'),],
        [InlineKeyboardButton(text="🇺🇿 Кирилча", callback_data='kiril'),],
        [InlineKeyboardButton(text="🇷🇺 Русский язык", callback_data='rus'),],
    ]
)