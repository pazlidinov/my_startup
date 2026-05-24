from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

client_main_menu=InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🔎 Skanerlash", web_app=WebAppInfo(url="https://scanner.pazlidinov.uz/")),], # type: ignore
        [InlineKeyboardButton(text="🔗 QR Codeni yangilash", callback_data='client_new_qrcode'),],
        [InlineKeyboardButton(text="💲 Balans", callback_data='client_balance'),],
        [InlineKeyboardButton(text="📈 Statistika", callback_data='client_statistics'),],
        [InlineKeyboardButton(text="🌐 Tilni o'zgartirish", callback_data='client_change_lang'),],
        # [InlineKeyboardButton(text="ℹ️ Info", callback_data='client_info'),],
    ]
)