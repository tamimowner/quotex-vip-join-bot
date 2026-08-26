import asyncio
import uvicorn
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from config import settings
from database.db import init_db
from handlers import setup_routers
from handlers.chat_member import router as chat_member_router
from postback import app as fastapi_app


async def start_bot():
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    # Include routers
    root_router = setup_routers()
    dp.include_router(root_router)
    dp.include_router(chat_member_router)

    # Init database
    await init_db()
    print("Database initialized")

    # Start polling
    print("Bot starting...")
    await dp.start_polling(bot)


def start_postback_server():
    uvicorn.run(
        fastapi_app,
        host=settings.HOST,
        port=settings.PORT,
        log_level="info"
    )


async def main():
    # Run both bot and FastAPI in the same process using asyncio
    # For production on Railway we recommend running them separately
    # or use a process manager. For simplicity we start bot here.
    await start_bot()


if __name__ == "__main__":
    asyncio.run(main())
