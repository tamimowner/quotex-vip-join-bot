"""
Entry point for Railway / Docker.
Runs FastAPI (postback) + aiogram bot together.
"""
import asyncio
import threading
import uvicorn
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from config import settings
from database.db import init_db
from handlers import setup_routers
from handlers.chat_member import router as chat_member_router
from postback import app as fastapi_app


def run_api():
    uvicorn.run(
        fastapi_app,
        host="0.0.0.0",
        port=int(settings.PORT),
        log_level="info"
    )


async def run_bot():
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    root_router = setup_routers()
    dp.include_router(root_router)
    dp.include_router(chat_member_router)

    await init_db()
    print("✅ Database ready")
    print("🤖 Bot polling started...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    # Start FastAPI in a background thread
    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()
    print(f"🌐 Postback server running on port {settings.PORT}")

    # Start bot in main thread
    asyncio.run(run_bot())
