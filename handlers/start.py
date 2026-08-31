import re
from datetime import datetime
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from sqlalchemy import select, func
from database.models import User, PostbackLog
from database.db import async_session
from keyboards import language_keyboard, main_menu, premium_keyboard, verify_fail_keyboard
from config import settings
from services.settings_store import get_affiliate_url, get_min_deposit, get_vip_group_link
from services.invite import create_unique_invite
from services.messages import get_message_text

router = Router()

# Quotex Trader ID = exactly 8 digits
TRADER_ID_RE = re.compile(r"^[0-9]{8}$")

_bot_name_cache: str | None = None


async def get_bot_display_name(bot: Bot) -> str:
    global _bot_name_cache
    if _bot_name_cache:
        return _bot_name_cache
    try:
        me = await bot.get_me()
        name = (me.full_name or me.first_name or me.username or "Bot").strip()
        _bot_name_cache = name
        return name
    except Exception as e:
        print(f"get_me failed: {e}")
        return "Bot"


async def _send_welcome(
    target: Message,
    lang: str,
    telegram_id: int,
    bot: Bot,
    reply_markup=None,
):
    bot_name = await get_bot_display_name(bot)
    register_url = await get_affiliate_url()
    text = await get_message_text(
        lang,
        "welcome",
        botName=bot_name,
        register_url=register_url,
    )
    # Welcome photo removed — text only
    await target.answer(
        text,
        reply_markup=reply_markup,
        parse_mode="HTML",
        disable_web_page_preview=True,
    )


@router.message(CommandStart())
async def cmd_start(message: Message, bot: Bot):
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
                await get_message_text("bn", "choose_language"),
                reply_markup=language_keyboard(),
            )
            return

        lang = user.language or "bn"
        await _send_welcome(
            message,
            lang,
            message.from_user.id,
            bot,
            reply_markup=await main_menu(lang),
        )


@router.callback_query(F.data.startswith("lang:"))
async def set_language(callback: CallbackQuery, bot: Bot):
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
        await callback.message.edit_text(await get_message_text(lang, "language_set"))
    except Exception:
        await callback.message.answer(await get_message_text(lang, "language_set"))
    await _send_welcome(
        callback.message,
        lang,
        callback.from_user.id,
        bot,
        reply_markup=await main_menu(lang),
    )
    await callback.answer()


@router.message(F.text.regexp(r"^[0-9]{8}$"))
async def receive_trader_id(message: Message, bot: Bot):
    trader_id = (message.text or "").strip()
    tg_id = message.from_user.id
    min_dep = await get_min_deposit()
    register_url = await get_affiliate_url()

    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == tg_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            await message.answer("Please /start first.")
            return

        lang = user.language or "bn"

        # --- Same ID already verified → just say already verified ---
        if user.is_verified and user.trader_id and user.trader_id == trader_id:
            await message.answer(
                await get_message_text(lang, "already_verified"),
                reply_markup=await main_menu(lang),
            )
            return

        # Check postback for THIS trader_id (do NOT save yet)
        pb_count = await session.scalar(
            select(func.count()).select_from(PostbackLog).where(
                PostbackLog.trader_id == trader_id
            )
        ) or 0

        dep_sum = float(
            await session.scalar(
                select(func.coalesce(func.sum(PostbackLog.sumdep), 0.0)).where(
                    PostbackLog.trader_id == trader_id
                )
            ) or 0
        )

        log_result = await session.execute(
            select(PostbackLog)
            .where(PostbackLog.trader_id == trader_id)
            .order_by(PostbackLog.id.desc())
            .limit(1)
        )
        last_log = log_result.scalar_one_or_none()

        # --- Invalid ID (no postback) → REJECT, do NOT save ---
        if pb_count == 0:
            await message.answer(
                await get_message_text(
                    lang,
                    "not_from_our_link",
                    trader_id=trader_id,
                    register_url=register_url,
                ),
                parse_mode="HTML",
                disable_web_page_preview=True,
                reply_markup=await verify_fail_keyboard(lang, register_url),
            )
            # Important: do NOT touch user.trader_id / is_verified / status
            return

        # From here ID is valid (has postback from our link)
        total = max(dep_sum, float(user.total_deposit or 0))

        # Account found but minimum deposit not reached
        if total < min_dep:
            user.trader_id = trader_id
            if last_log and last_log.country:
                user.country = last_log.country
            if total > float(user.total_deposit or 0):
                user.total_deposit = total
                user.last_deposit = total
            await session.commit()

            await message.answer(
                await get_message_text(
                    lang,
                    "account_ok_need_deposit",
                    trader_id=trader_id,
                    min_deposit=int(min_dep),
                ),
                parse_mode="HTML",
                reply_markup=await premium_keyboard(lang, register_url),
            )
            return

        # Valid ID + deposit OK → verify / re-verify with new ID
        user.trader_id = trader_id
        if last_log and last_log.country:
            user.country = last_log.country
        if total > float(user.total_deposit or 0):
            user.total_deposit = total
            user.last_deposit = total

        if not user.is_verified:
            user.is_verified = True
            user.verified_at = datetime.utcnow()

        await session.commit()

        # Create new unique invite link
        vip_link = await create_unique_invite(bot, tg_id)
        if not vip_link:
            vip_link = await get_vip_group_link()

        if vip_link:
            user.invite_link = vip_link
            await session.commit()

            await message.answer(
                await get_message_text(
                    lang,
                    "invite_ready",
                    link=vip_link,
                    trader_id=trader_id,
                ),
                parse_mode="HTML",
                disable_web_page_preview=True,
            )
        else:
            await message.answer(
                await get_message_text(lang, "already_verified"),
                reply_markup=await main_menu(lang),
            )


@router.message(F.text)
async def fallback_text(message: Message):
    """Any typed message (not command / not trader id) shows main menu again."""
    text = (message.text or "").strip()
    if text.startswith("/"):
        return

    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()
        lang = (user.language if user else None) or "bn"

    # Looks like bad trader id attempt
    if any(ch.isdigit() for ch in text) or len(text) <= 20:
        if not TRADER_ID_RE.match(text):
            await message.answer(
                await get_message_text(lang, "invalid_trader_id"),
                parse_mode="HTML",
                reply_markup=await main_menu(lang),
            )
            return

    # Normal typed message → bring menu buttons back
    await message.answer(
        await get_message_text(lang, "main_menu"),
        reply_markup=await main_menu(lang),
    )
