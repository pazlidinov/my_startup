from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

gym_main_menu=InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🔎 Skanerlash", web_app=WebAppInfo(url="https://your-domain.com")),],
        [InlineKeyboardButton(text="💶 Bir kunlik to'lov", callback_data='gym_lum_sum'),],
        [InlineKeyboardButton(text="💲 Balans", callback_data='gym_balance'),],
        [InlineKeyboardButton(text="📈 Statistika", callback_data='gym_statistics'),],
        [InlineKeyboardButton(text="⚙️ Sozlamalar", callback_data='gym_settings'),],
        # [InlineKeyboardButton(text="ℹ️ Info", callback_data='gym_info'),],
    ]
)

gym_settings_menu=InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="👥 Hodimlar", callback_data='gym_worker'),],
        [InlineKeyboardButton(text="💷 Bir kunlik to'lovni o'zgartirish", callback_data='gym_change_lump_sum'),],
        [InlineKeyboardButton(text="📍 Joylashuvni o'zgartirish", callback_data='gym_change_location'),],       
        [InlineKeyboardButton(text="🔗 QR Codeni yangilash", callback_data='gym_new_qrcode'),],
        [InlineKeyboardButton(text="🌐 Tilni o'zgartirish", callback_data='gym_change_lang'),],
        [InlineKeyboardButton(text="🔙 Menu", callback_data="menu_gym"),],
    ]
)


gym_back_settings=InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="⚙️ Sozlamalar", callback_data='gym_settings'),],
    ]
)