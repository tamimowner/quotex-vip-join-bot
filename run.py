"""
Entry point for Railway / Docker.
Runs FastAPI (postback) + aiogram bot together.
"""
import asyncio
import os
import threading
import traceback
import uvicorn
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from config import settings
from database.db import init_db
from handlers import setup_routers
from postback import app as fastapi_app


def get_port() -> int:
    return int(os.getenv("PORT", str(settings.PORT or 8000)))


def run_api():
    port = get_port()
    print(f"Starting uvicorn on 0.0.0.0:{port}")
    uvicorn.run(
        fastapi_app,
        host="0.0.0.0",
        port=port,
        log_level="info",
    )


async def run_bot():
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    # setup_routers() already includes start, menu, chat_member — include once only
    dp.include_router(setup_routers())

    await init_db()
    print("Database ready")
    print("Bot polling started...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    port = get_port()
    print(f"PORT={port}")
    print(f"DATABASE_URL scheme ok={settings.database_url.startswith('postgresql+asyncpg')}")

    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()
    print(f"Postback server thread started on port {port}")

    try:
        asyncio.run(run_bot())
    except Exception:
        print("Bot crashed:")
        traceback.print_exc()
        api_thread.join()
