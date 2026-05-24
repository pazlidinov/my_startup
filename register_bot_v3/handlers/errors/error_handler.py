import logging

from aiogram import Router
from aiogram.types import ErrorEvent
from aiogram.exceptions import (
    TelegramUnauthorizedError,
    TelegramBadRequest,
    TelegramForbiddenError,
    TelegramRetryAfter,
    TelegramNetworkError,
    TelegramAPIError,
)

router = Router()


@router.error()
async def error_handler(event: ErrorEvent):
    exception = event.exception

    # Chat creator bilan muammo
    if "chat creator" in str(exception).lower():
        logging.exception("Can't demote chat creator")
        return True

    # Message not modified
    if isinstance(exception, TelegramBadRequest):
        logging.exception(f"BadRequest: {exception}")
        return True

    # Unauthorized
    if isinstance(exception, TelegramUnauthorizedError):
        logging.exception(f"Unauthorized: {exception}")
        return True

    # Retry after (flood control)
    if isinstance(exception, TelegramRetryAfter):
        logging.exception(f"RetryAfter: {exception}")
        return True

    # Network error
    if isinstance(exception, TelegramNetworkError):
        logging.exception(f"NetworkError: {exception}")
        return True

    # Boshqa Telegram xatolar
    if isinstance(exception, TelegramAPIError):
        logging.exception(f"TelegramAPIError: {exception}")
        return True

    # Default
    logging.exception(f"Unhandled error: {exception}")
    return True
