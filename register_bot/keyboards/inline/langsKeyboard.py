from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def langs(role):
    langskey = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🇺🇿 O'zbek tilida", callback_data=f"{role}_lang_lotin"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🇺🇿 Кирилча", callback_data=f"{role}_lang_kiril"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🇷🇺 Русский язык", callback_data=f"{role}_lang_rus"
                ),
            ],
        ]
    )
    return langskey
