"""
Railway entry: FastAPI (postback) + aiogram on ONE asyncio event loop.
(Threading uvicorn caused SQLAlchemy 'Future attached to a different loop'.)
"""
import asyncio
import os
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


async def run_bot() -> None:
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()
    dp.include_router(setup_routers())
    print("Bot polling started...")
    await dp.start_polling(bot)


async def main() -> None:
    port = get_port()
    print(f"PORT={port}")
    print(
        "DATABASE_URL scheme ok="
        f"{settings.database_url.startswith('postgresql+asyncpg')}"
    )

    await init_db()
    print("Database ready")

    config = uvicorn.Config(
        fastapi_app,
        host="0.0.0.0",
        port=port,
        log_level="info",
        loop="asyncio",
    )
    server = uvicorn.Server(config)

    await asyncio.gather(server.serve(), run_bot())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception:
        print("Fatal crash:")
        traceback.print_exc()
        raise
