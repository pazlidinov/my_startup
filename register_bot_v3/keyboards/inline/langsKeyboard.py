from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def langs(role, with_back_menu=False, with_back_settins=False):
    langskey = [
        [
            InlineKeyboardButton(
                text="🇺🇿 O'zbek tilida", callback_data=f"{role}_lang_lotin"
            ),
        ],
        [
            InlineKeyboardButton(text="🇺🇿 Кирилча", callback_data=f"{role}_lang_kiril"),
        ],
        [
            InlineKeyboardButton(
                text="🇷🇺 Русский язык", callback_data=f"{role}_lang_rus"
            ),
        ],
    ]
    if with_back_settins:
        langskey.append(
            [InlineKeyboardButton(text="⚙️ Sozlamalar", callback_data="gym_settings")]
        )
    if with_back_menu:
        langskey.append(
            [InlineKeyboardButton(text="🔙 Menu", callback_data=f"menu_{role}")]
        )
    return InlineKeyboardMarkup(inline_keyboard=langskey)
