from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton


def get_worker_key(show_key: bool, worker_list: dict):
    builder = InlineKeyboardBuilder()

    if show_key:
        for key, value in worker_list.items():
            builder.button(
                text=f"❌ {key} o'chirish",
                callback_data=f"gym_woker_delete_{value}",
            )

        if len(worker_list) < 4:
            builder.button(text="➕ Qo'shish", callback_data="gym_worker_plus")

    builder.button(text="⚙️ Sozlamalar", callback_data="gym_settings")
    builder.button(text="🔙 Menu", callback_data="menu_gym")

    # 🔥 row_width o‘rniga adjust ishlatiladi
    builder.adjust(2)  # har qatorda 2 ta tugma

    return builder.as_markup()
