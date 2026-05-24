from aiogram import Router

from . import help, start, menu, gym_settings, for_client, for_gym, echo

router = Router()

# router.include_router(help.router)
router.include_router(start.router)
router.include_router(menu.router)
router.include_router(gym_settings.router)
router.include_router(for_client.router)
router.include_router(for_gym.router)
router.include_router(echo.router)