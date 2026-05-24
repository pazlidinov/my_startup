from aiogram import Bot
from aiogram.types import BotCommand

COMMANDS = [
    BotCommand(command="start", description="Botni ishga tushurish"),
    BotCommand(command="menu", description="Menu"),
    # BotCommand(command="help", description="Yordam"),
]


async def set_default_commands(bot: Bot):
    await bot.set_my_commands(COMMANDS)