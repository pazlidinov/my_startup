from aiogram import Router

from . import errors, users, groups, channels

router = Router()

# har bir modul ichidagi routerlarni ulaymiz
router.include_router(errors.router)
router.include_router(users.router)
router.include_router(groups.router)
router.include_router(channels.router)