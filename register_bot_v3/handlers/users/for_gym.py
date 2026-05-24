from datetime import date
import logging
from pathlib import Path

from aiogram import Router, F
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    InputFile,
    FSInputFile,
    BufferedInputFile,
)

from keyboards.inline import menu_gym, monthsKeyboard
from utils.others.diagram_for_statistics import create_chart, sort_by_day
from utils.db_api.database import all_tables as db

router = Router()

BASE_DIR = Path(__file__).resolve().parent.parent.parent
MEDIA_DIR = BASE_DIR / "qr_code_img"
MEDIA_DIR.mkdir(parents=True, exist_ok=True)
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


@router.callback_query(F.data == "gym_lum_sum")
async def gym_lum_sum(call: CallbackQuery):
    await call.answer()
    confirm_lump_sum = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Ha", callback_data="confirm_lum_sum_yes"),
                InlineKeyboardButton(
                    text="❌ Yo'q", callback_data="confirm_lum_sum_no"
                ),
            ],
        ]
    )
    await call.message.delete()
    return await call.message.answer(
        "⚠️ Bir kunlik to'lov qlishni tasdiqlayszimi?", reply_markup=confirm_lump_sum
    )


@router.callback_query(F.data.startswith("confirm_lum_sum_"))
async def confirm_lum_sum(call: CallbackQuery):
    await call.answer()
    answer_confirm = call.data.split("_")[-1]
    if answer_confirm == "no":
        await call.message.delete()
        await call.message.answer("❗ Bir kunlik to'lov bekor qilindi.")
        return await call.message.answer_photo(
            photo=FSInputFile(MEDIA_DIR / f"{call.from_user.id}.png"),
            caption="⬆️ QrCodeni mijozga ko'rsating\n⬇️ Mijozning QrCodeni skanerlang",
            reply_markup=menu_gym.gym_main_menu,
        )
    try:
        gym = dict(await db.select_gym_by_worker(telegram_id=str(call.from_user.id)))
    except Exception as err:
        logging.exception(err)
        return await call.message.answer(
            "❗ Xatolik yuz berdi, iltimos qayta urinib ko'ring."
        )

    if not gym["is_active"]:
        return await call.message.answer(
            "❗ Sport zal aktiv holatda emas. Iltimos balansingizni tekshiring."
        )
    try:
        payment_id = await db.add_payment_for_lump_sum(
            gym_id=gym["gym_id"], lump_sum=gym["lump_sum"]
        )
        await db.add_registration_for_lump_sum(
            gym_id=gym["gym_id"], payment_id=payment_id
        )
        all_worker = await db.sort_worker_by_gym(telegram_id=str(call.from_user.id))
        for item in all_worker:
            if item["telegram_id"] == str(call.from_user.id):
                await call.message.delete()
                await call.message.answer(
                    "✅ Tabriklaymiz, bir kunlik to'lov qabul qilindi."
                )
                await call.message.answer_photo(
                    photo=FSInputFile(MEDIA_DIR / f"{call.from_user.id}.png"),
                    caption="⬆️ QrCodeni mijozga ko'rsating\n⬇️ Mijozning QrCodeni skanerlang",
                    reply_markup=menu_gym.gym_main_menu,
                )
                continue
            await call.bot.send_message(
                chat_id=item["telegram_id"],
                text=f"✅ <a href='tg://user?id={item['telegram_id']}'>"
                + f"{call.from_user.first_name}</a> "
                + f"tomonidan bir kunlik to'lov qabul qilindi.",
                parse_mode="HTML",
                disable_web_page_preview=True,
            )
    except Exception as err:
        logging.exception(err)
        return await call.message.answer(
            "❗ Xatolik yuz berdi, iltimos qayta urinib ko'ring."
        )


@router.callback_query(F.data == "gym_balance")
async def gym_balance(call: CallbackQuery):
    await call.answer()
    try:
        info_gym = dict(await db.balance_gym(telegram_id=str(call.from_user.id)))
        info_admin = await db.select_admin()
        group_link_key = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Guruhga kirish",
                        url=info_admin["gym_group_link"],
                    ),
                ],
                [
                    InlineKeyboardButton(text="🔙 Menu", callback_data="menu_gym"),
                ],
            ]
        )
        await call.message.answer(
            text=f"<b>✏️ <a href='https://maps.google.com/?q={info_gym['loc_lat']},{info_gym['loc_long']}'>{info_gym['name']}</a></b>\n"
            + f"<b>🆔 ID:</b> {info_gym['id']}\n"
            + f"<b>💲 Balans:</b> {info_gym['balance']} so'm\n"
            + f"<b>🗓️ Muddati:</b> {info_gym['date_end']}\n"
            + f"<b>⭕ Faolligi:</b> {'✅ Foal' if info_gym['is_active'] else '❌ Foal emas'}"
            + f"\n\n\n"
            + f"<b>💲 To'lov uchun:</b>\n"
            + f"💳 {info_admin['card_number']}\n"
            + f"📇 {info_admin['card_name']}\n"
            + f"<b>💶 Oylik to'lov:</b> {info_admin['amount']} so'm\n\n"
            + f"<b>ℹ️ Eslatma:</b> To'lov cheki va zal 🆔 ID\n"
            + f"quyidagi guruhga yuboring\n",
            reply_markup=group_link_key,
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
        await call.message.delete()
    except Exception as err:
        logging.exception(err)
        await call.message.answer("❗ Xatolik yuz berdi, iltimos qayta urinib ko'ring.")


@router.callback_query(F.data.startswith("gym_statistics"))
async def gym_statistics_by_month(call: CallbackQuery):
    await call.answer()
    if "month" in call.data:
        data_date = call.data.split("_")[-1]
        year = int(data_date.split("-")[0])
        month = int(data_date.split("-")[1])
    else:
        today = date.today()
        year = int(today.year)
        month = int(today.month)
    try:
        registration_by_month = await db.select_registrations_by_worker(
            telegram_id=str(call.from_user.id), year=year, month=month
        )
        payments_by_month = await db.select_payment_by_worker(
            telegram_id=str(call.from_user.id), year=year, month=month
        )
    except Exception as err:
        logging.exception(err)
        return await call.answer("❗ Xatolik yuz berdi, iltimos qayta urinib ko'ring.")
    await call.message.delete()
    if registration_by_month:
        result_by_regitrtion = sort_by_day(sql_response=registration_by_month)
        registration_img = create_chart(
            data=result_by_regitrtion, year=year, month=all_months[month - 1]
        )
        await call.message.answer_photo(
            photo=BufferedInputFile(registration_img.getvalue(), filename="reg.png"),
            caption="📊 Mijozlar oqimi",
        )
    if payments_by_month:
        result_by_payments = sort_by_day(sql_response=payments_by_month)
        payments_img = create_chart(
            data=result_by_payments,
            year=year,
            month=all_months[month - 1],
            payments=True,
        )
        await call.message.answer_photo(
            photo=BufferedInputFile(payments_img.getvalue(), filename="pay.png"),
            caption="💰 To'lovlar",
        )
    if not registration_by_month and not payments_by_month:
        send_text = f"🚫 {year}-yil {all_months[month-1]} oyida ma'lumotlar topilmadi"
    else:
        send_text = "📋 Kerakli oyni tanlang."
    await call.message.answer(
        text=send_text,
        reply_markup=monthsKeyboard.get_months_key("gym", "statistics"),
    )


@router.callback_query(F.data == "gym_settings")
async def gym_settigs(call: CallbackQuery):
    await call.answer()
    try:
        await db.update_gym_by_worker(
            telegram_id=str(call.from_user.id),
            waiting_lump_sum=False,
            waiting_location=False,
        )
    except Exception as err:
        logging.exception(err)
        await call.message.answer("❗ Xatolik yuz berdi, iltimos qayta urinib ko'ring.")
    await call.message.delete()
    await call.message.answer(
        text="⚙️ Sozlamalar", reply_markup=menu_gym.gym_settings_menu
    )
