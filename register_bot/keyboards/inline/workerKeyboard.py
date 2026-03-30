from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_worker_key(show_key: bool, worker_list: dict):
    worker_key = InlineKeyboardMarkup(row_width=2)
    if show_key:
        for key, value in worker_list.items():
            worker_key.insert(
                InlineKeyboardButton(
                    text=f"❌ {key} o'chirish",
                    callback_data=f"gym_woker_delete_{value}",
                )
            )
        if len(worker_list) < 4:
            worker_key.add(
                InlineKeyboardButton(
                    text="➕ Qo'shish", callback_data="gym_worker_plus"
                )
            )

    worker_key.add(
        InlineKeyboardButton(text="⚙️ Sozlamalar", callback_data="gym_settings")
    )
    worker_key.add(InlineKeyboardButton(text="🔙 Menu", callback_data="menu_gym"))
    return worker_key
