import re
from datetime import datetime
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from sqlalchemy import select, func
from database.models import User, PostbackLog
from database.db import async_session
from keyboards import language_keyboard, main_menu, premium_keyboard
from locales import get_text
from config import settings
from services.settings_store import get_setting, get_affiliate_url
from services.invite import create_unique_invite

router = Router()

BOT_DISPLAY_NAME = "RT VIP JOIN BOT"
TRADER_ID_RE = re.compile(r"^[0-9]{8}$")
MIN_DEPOSIT = 20.0


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

    try:
        await callback.message.edit_text(get_text(lang, "language_set"))
    except Exception:
        await callback.message.answer(get_text(lang, "language_set"))
    await _send_welcome(
        callback.message,
        lang,
        reply_markup=await main_menu(lang),
    )
    await callback.answer()


@router.message(F.text.regexp(r"^[0-9]{8}$"))
async def receive_trader_id(message: Message, bot: Bot):
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

        # Sum deposits from postback logs for this trader_id
        dep_sum = await session.scalar(
            select(func.coalesce(func.sum(PostbackLog.sumdep), 0.0)).where(
                PostbackLog.trader_id == trader_id
            )
        )
        dep_sum = float(dep_sum or 0)

        # Also check click_id = telegram_id logs
        dep_by_click = await session.scalar(
            select(func.coalesce(func.sum(PostbackLog.sumdep), 0.0)).where(
                PostbackLog.click_id == str(message.from_user.id)
            )
        )
        dep_by_click = float(dep_by_click or 0)
        total = max(dep_sum, dep_by_click, float(user.total_deposit or 0))

        # Latest country from postback
        log_result = await session.execute(
            select(PostbackLog)
            .where(
                (PostbackLog.trader_id == trader_id)
                | (PostbackLog.click_id == str(message.from_user.id))
            )
            .order_by(PostbackLog.id.desc())
            .limit(1)
        )
        last_log = log_result.scalar_one_or_none()
        if last_log and last_log.country:
            user.country = last_log.country

        if total > float(user.total_deposit or 0):
            user.total_deposit = total
            user.last_deposit = total

        already = user.is_verified
        if total >= MIN_DEPOSIT and not user.is_verified:
            user.is_verified = True
            user.verified_at = datetime.utcnow()

        await session.commit()

        if user.is_verified and not user.has_joined:
            invite_link = user.invite_link
            if not invite_link:
                invite_link = await create_unique_invite(bot, message.from_user.id)
            if invite_link:
                await message.answer(
                    get_text(lang, "invite_ready", link=invite_link),
                    parse_mode="HTML",
                    disable_web_page_preview=True,
                    reply_markup=await main_menu(lang),
                )
                return

        if already or user.is_verified:
            await message.answer(
                get_text(lang, "already_verified"),
                reply_markup=await main_menu(lang),
            )
            return

        # Not verified yet — show register link
        register_url = await get_affiliate_url(str(message.from_user.id))
        await message.answer(
            get_text(lang, "trader_id_saved", trader_id=trader_id)
            + "\n\n"
            + get_text(lang, "need_deposit_hint", min_deposit=int(MIN_DEPOSIT)),
            parse_mode="HTML",
            reply_markup=await premium_keyboard(lang, register_url),
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
