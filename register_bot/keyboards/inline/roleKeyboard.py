from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

roles=InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🏋️‍♂️ Yangi sport zal uchun", callback_data='director'),],
        [InlineKeyboardButton(text="🧑‍💻 Ishchi hodim", callback_data='worker'),],
        [InlineKeyboardButton(text="👥 Mijoz sifatida", callback_data='client'),],
    ]
)