from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

gym_main_menu=InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🔎 Skanerlash", callback_data='gym_scaner'),],
        [InlineKeyboardButton(text="💶 Bir kunlik to'lov", callback_data='gym_lum_sum'),],
        [InlineKeyboardButton(text="💵 Balans", callback_data='gym_balance'),],
        [InlineKeyboardButton(text="📈📊 Statistika", callback_data='gym_statics'),],
        [InlineKeyboardButton(text="⚙️ Sozlamalar", callback_data='gym_settings'),],
    ]
)

gym_sub_menu=InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="👨‍👦‍👦 Hodimlar", callback_data='gym_worker'),],
        [InlineKeyboardButton(text="💷 Bir kunlik to'ni o'zgartirish", callback_data='gym_change_lum_sum'),],
        [InlineKeyboardButton(text="📍 Lokatsiyani o'zgartirish", callback_data='gym_change_location'),],       
        [InlineKeyboardButton(text="🌐 Tilni o'zgartirish", callback_data='gym_change_lang'),],
    ]
)