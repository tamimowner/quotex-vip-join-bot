from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from sqlalchemy import select
from database.models import User
from database.db import async_session
from keyboards import language_keyboard, main_menu
from locales import get_text
from config import settings

router = Router()


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
        name = message.from_user.first_name or "User"
        await message.answer(
            get_text(lang, "welcome", name=name),
            reply_markup=await main_menu(lang),
            parse_mode="HTML",
        )


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
    name = callback.from_user.first_name or "User"
    await callback.message.answer(
        get_text(lang, "welcome", name=name),
        reply_markup=await main_menu(lang),
        parse_mode="HTML",
    )
    await callback.answer()
