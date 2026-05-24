import asyncio
import aiohttp

async def fix():
    TOKEN = "8446190199:AAGn2OtIjYzGRpcm8epGDtqygjTl7KaqK3Q"
    async with aiohttp.ClientSession() as session:
        # getUpdates orqali allowed_updates ni yangilash
        r = await session.post(
            f"https://api.telegram.org/bot{TOKEN}/getUpdates",
            json={
                "allowed_updates": ["message", "web_app_data"],
                "timeout": 1
            }
        )
        print(await r.json())

asyncio.run(fix())