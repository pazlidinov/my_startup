from aiogram import Router, F
from aiogram.types import Message

from aiogram.fsm.context import FSMContext

router = Router()


@router.message(F.text)
async def bot_echo(message: Message, state: FSMContext):

    await message.answer(message.text)
