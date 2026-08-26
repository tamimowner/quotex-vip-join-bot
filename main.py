import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from config import settings
from database.db import init_db
from handlers import setup_routers


async def start_bot():
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()
    dp.include_router(setup_routers())

    await init_db()
    print("Database initialized")
    print("Bot starting...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(start_bot())
