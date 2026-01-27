from datetime import date
from loader import dp
from aiogram import types
from keyboards.inline import langsKeyboard, menu_gym, monthsKeyboard
from utils.others.secret_code import generate_code
from utils.others.qr_code import generate_qr_code
from utils.db_api.database import all_tables as db
import logging
import os
from pathlib import Path
from aiogram.types import InlineKeyboardButton
