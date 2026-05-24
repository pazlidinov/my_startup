import asyncio
from aiogram import BaseMiddleware
from collections import defaultdict


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, delay: float = 1.0):
        self.delay = delay
        self.user_timers = defaultdict(float)
        super().__init__()

    async def __call__(self, handler, event, data):
        user_id = None

        if hasattr(event, "from_user"):
            user_id = event.from_user.id

        if user_id:
            now = asyncio.get_event_loop().time()
            last_time = self.user_timers[user_id]

            if now - last_time < self.delay:
                return  # skip spam

            self.user_timers[user_id] = now

        return await handler(event, data)
