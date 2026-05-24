import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher
from loader import bot
import middlewares, filters, handlers
from middlewares import ThrottlingMiddleware
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands
from utils.db_api.database import all_tables

# ✅ QR ma'lumotini qabul qiluvchi endpoint
async def api_qr(request):
    print('ok')
    data = await request.json()
    init_data = data.get("init_data", "")
    qr_text = data.get("qr_text", "")

    # initData dan user_id olish
    user_id = None
    for part in init_data.split("&"):
        if part.startswith("user="):
            import json, urllib.parse
            user_json = urllib.parse.unquote(part[5:])
            user_id = json.loads(user_json).get("id")
            break

    if user_id:
        await bot.send_message(user_id, f"📷 Skanerlandi:\n{qr_text}")

    return web.json_response({"ok": True})

async def on_startup(bot: Bot):
    await all_tables.connect()
    await set_default_commands(bot)
    await on_startup_notify(bot)

async def main():
    dp = Dispatcher()
    dp.update.middleware(ThrottlingMiddleware())
    dp.include_router(handlers.router)
    await on_startup(bot)

    # ✅ Aiohttp server
    app = web.Application()
    app.router.add_post("/api/qr", api_qr)

    CORS - WebApp dan so'rov kelishi uchun
    async def cors_handler(request):
        return web.Response(headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type"
        })
    app.router.add_route("OPTIONS", "/api/qr", cors_handler)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()

    print("✅ Server: http://localhost:8080")
    print("✅ Bot ishga tushdi!")

    await dp.start_polling(
        bot,
        allowed_updates=["message", "callback_query"]
    )

if __name__ == "__main__":
    asyncio.run(main())