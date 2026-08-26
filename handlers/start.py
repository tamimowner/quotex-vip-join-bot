import re
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import CommandStart
from sqlalchemy import select
from database.models import User
from database.db import async_session
from keyboards import language_keyboard, main_menu
from locales import get_text
from config import settings
from services.settings_store import get_setting

router = Router()

BOT_DISPLAY_NAME = "RT VIP JOIN BOT"
TRADER_ID_RE = re.compile(r"^[0-9]{8}$")


async def _send_welcome(target: Message, lang: str, reply_markup=None):
    text = get_text(lang, "welcome", botName=BOT_DISPLAY_NAME)
    file_id = await get_setting("welcome_photo_file_id", "")
    photo_url = await get_setting("welcome_photo_url", "")

    try:
        if file_id:
            await target.answer_photo(
                photo=file_id,
                caption=text,
                reply_markup=reply_markup,
                parse_mode="HTML",
            )
            return
        if photo_url:
            await target.answer_photo(
                photo=photo_url,
                caption=text,
                reply_markup=reply_markup,
                parse_mode="HTML",
            )
            return
    except Exception as e:
        print(f"Welcome photo failed: {e}")

    await target.answer(
        text,
        reply_markup=reply_markup,
        parse_mode="HTML",
    )


@router.message(CommandStart())
async def cmd_start(message: Message):
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()

        if not user:
            user = User(
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                full_name=message.from_user.full_name,
                language=settings.DEFAULT_LANGUAGE,
            )
            session.add(user)
            await session.commit()
            await message.answer(
                get_text("bn", "choose_language"),
                reply_markup=language_keyboard(),
            )
            return

        lang = user.language or "bn"
        await _send_welcome(message, lang, reply_markup=await main_menu(lang))


@router.callback_query(F.data.startswith("lang:"))
async def set_language(callback: CallbackQuery):
    lang = callback.data.split(":")[1]
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == callback.from_user.id)
        )
        user = result.scalar_one_or_none()
        if user:
            user.language = lang
            await session.commit()

    await callback.message.edit_text(get_text(lang, "language_set"))
    await _send_welcome(
        callback.message,
        lang,
        reply_markup=await main_menu(lang),
    )
    await callback.answer()


@router.message(F.text.regexp(r"^[0-9]{8}$"))
async def receive_trader_id(message: Message):
    trader_id = (message.text or "").strip()
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()
        if not user:
            await message.answer("Please /start first.")
            return

        lang = user.language or "bn"
        user.trader_id = trader_id
        await session.commit()

        await message.answer(
            get_text(lang, "trader_id_saved", trader_id=trader_id),
            parse_mode="HTML",
            reply_markup=await main_menu(lang),
        )


@router.message(F.text)
async def fallback_text(message: Message):
    text = (message.text or "").strip()
    if text.startswith("/"):
        return

    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()
        lang = (user.language if user else None) or "bn"

    if any(ch.isdigit() for ch in text) or len(text) <= 20:
        if not TRADER_ID_RE.match(text):
            await message.answer(
                get_text(lang, "invalid_trader_id"),
                parse_mode="HTML",
            )
