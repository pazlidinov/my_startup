from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

gym_main_menu=InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Skanerlash", callback_data='gym_scaner'),],
        [InlineKeyboardButton(text="Bir kunlik to'lov", callback_data='gym_lum_sum'),],
        [InlineKeyboardButton(text="Balans", callback_data='gym_balance'),],
        [InlineKeyboardButton(text="Statistika", callback_data='gym_balance'),],
        [InlineKeyboardButton(text="Sozlamalar", callback_data='gym_settings'),],
    ]
)

gym_sub_menu=InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Hodim qo'shish", callback_data='gym_add_worker'),],
        [InlineKeyboardButton(text="Bir kunlik to'lov o'zgartirish", callback_data='gym_change_lum_sum'),],
        [InlineKeyboardButton(text="Balans", callback_data='gym_balance'),],
        [InlineKeyboardButton(text="Statistika", callback_data='gym_balance'),],
        [InlineKeyboardButton(text="Sozlamalar", callback_data='gym_settings'),],
    ]
)