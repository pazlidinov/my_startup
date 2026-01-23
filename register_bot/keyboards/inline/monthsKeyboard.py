from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from utils.others.get_months import get_12_months

all_months = [
    "Yanvar",
    "Fevral",
    "Mart",
    "Aprel",
    "May",
    "Iyun",
    "Iyul",
    "Avgust",
    "Sentabr",
    "Oktyabr",
    "Noyabr",
    "Dekabr",
]


def get_months_key(role, section):
    get_months = get_12_months()
    months_key = InlineKeyboardMarkup(row_width=2)

    for item in get_months:
        months_key.insert(
            InlineKeyboardButton(
                text=f"{all_months[int(item[-2::])-1]} {item[:4]}",
                callback_data=f"{role}_{section}_month_{item}",
            )
        )
    months_key.insert(InlineKeyboardButton(text="🔙 Menu", callback_data=f"menu_{role}"))
    return months_key
