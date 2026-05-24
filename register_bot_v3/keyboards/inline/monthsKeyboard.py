from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

from utils.others.get_months import get_12_months

all_months = [
    "Yanvar", "Fevral", "Mart", "Aprel", "May", "Iyun",
    "Iyul", "Avgust", "Sentabr", "Oktyabr", "Noyabr", "Dekabr",
]


def get_months_key(role, section):
    months = get_12_months()

    builder = InlineKeyboardBuilder()

    for item in months:
        builder.button(
            text=f"{all_months[int(item[-2:]) - 1]} {item[:4]}",
            callback_data=f"{role}_{section}_month_{item}",
        )

    # 🔙 Menu tugmasi
    builder.button(
        text="🔙 Menu",
        callback_data=f"menu_{role}"
    )

    # 🔥 row_width o‘rniga
    builder.adjust(2)

    return builder.as_markup()