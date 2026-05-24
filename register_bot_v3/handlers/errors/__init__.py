from aiogram import Router

from . import error_handler

router = Router()

router.include_router(error_handler.router)