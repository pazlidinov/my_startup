import asyncio
import json
import urllib.parse
from aiohttp import web
from aiogram import Bot, Dispatcher
from loader import bot  # bot obyekti va token loader.py dan kelmoqda
import handlers  # handlerlarni import qilish

# ✅ QR ma'lumotini qabul qiluvchi endpoint
async def api_qr(request):
    print("--- Yangi so'rov keldi ---")
    try:
        data = await request.json()
        init_data = data.get("init_data", "")
        qr_text = data.get("qr_text", "")

        print(f"Skanerlangan matn: {qr_text}")

        # initData dan user_id ni xavfsiz olish
        user_id = None
        if init_data:
            params = dict(urllib.parse.parse_qsl(init_data))
            if "user" in params:
                user_data = json.loads(params["user"])
                user_id = user_data.get("id")

        if user_id:
            try:
                await bot.send_message(user_id, f"📷 QR Kod skanerlandi:\n\n`{qr_text}`", parse_mode="Markdown")
                print(f"✅ Xabar yuborildi: {user_id}")
            except Exception as e:
                print(f"❌ Bot xabar yubora olmadi: {e}")
        else:
            print("⚠️ User ID topilmadi (initData xato yoki bo'sh)")

        return web.json_response({"ok": True, "status": "sent"})

    except Exception as e:
        print(f"❌ Server ichki xatosi: {e}")
        return web.json_response({"ok": False, "error": str(e)}, status=500)

# ✅ CORS Middleware (Brauzer bloklamasligi uchun)
async def cors_middleware(app, handler):
    async def middleware(request):
        if request.method == "OPTIONS":
            return web.Response(headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, ngrok-skip-browser-warning",
            })
        response = await handler(request)
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response
    return middleware

async def main():
    # Dispatcher sozlamalari
    dp = Dispatcher()
    dp.include_router(handlers.router)

    # Aiohttp ilovasi
    app = web.Application(middlewares=[cors_middleware])
    app.router.add_post("/api/qr", api_qr)

    # Serverni sozlash
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()

    print("🚀 API Server: http://localhost:8080")
    print("🤖 Bot polling rejimida ishga tushdi...")

    # Bot va API ni birga ishga tushirish
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("To'xtatildi")