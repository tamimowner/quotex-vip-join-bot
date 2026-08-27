from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy import select, or_
from database.models import User, PostbackLog
from database.db import async_session
from keyboards import (
    main_menu,
    premium_keyboard,
    back_keyboard,
    settings_keyboard,
    settings_language_keyboard,
)
from locales import get_text
from services.settings_store import (
    get_affiliate_url,
    get_setting,
    get_support_text,
    get_min_deposit,
    get_vip_group_link,
)

router = Router()

BOT_DISPLAY_NAME = "RT VIP JOIN BOT"


async def get_user(telegram_id: int) -> User | None:
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()


async def _safe_edit(callback: CallbackQuery, text: str, reply_markup=None):
    try:
        await callback.message.edit_text(
            text,
            reply_markup=reply_markup,
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
    except Exception:
        await callback.message.answer(
            text,
            reply_markup=reply_markup,
            parse_mode="HTML",
            disable_web_page_preview=True,
        )


@router.callback_query(F.data == "menu:back")
async def menu_back(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)
    lang = user.language if user else "bn"
    text = get_text(lang, "welcome", botName=BOT_DISPLAY_NAME)
    await _safe_edit(callback, text, reply_markup=await main_menu(lang))
    await callback.answer()


@router.callback_query(F.data == "menu:settings")
async def menu_settings(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)
    lang = user.language if user else "bn"
    await _safe_edit(
        callback,
        get_text(lang, "settings_title"),
        reply_markup=await settings_keyboard(lang),
    )
    await callback.answer()


@router.callback_query(F.data == "settings:lang")
async def settings_lang(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)
    lang = user.language if user else "bn"
    await _safe_edit(
        callback,
        get_text(lang, "choose_language"),
        reply_markup=await settings_language_keyboard(lang),
    )
    await callback.answer()


@router.callback_query(F.data == "menu:premium")
async def menu_premium(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)
    lang = user.language if user else "bn"

    # Already verified → show static VIP link
    if user and user.is_verified:
        vip_link = await get_vip_group_link() or user.invite_link
        if vip_link:
            await _safe_edit(
                callback,
                get_text(lang, "invite_ready", link=vip_link),
                reply_markup=await back_keyboard(lang),
            )
            await callback.answer()
            return

    if user and user.has_joined:
        await _safe_edit(
            callback,
            get_text(lang, "already_joined"),
            reply_markup=await back_keyboard(lang),
        )
        await callback.answer()
        return

    register_url = await get_affiliate_url(str(callback.from_user.id))
    await _safe_edit(
        callback,
        get_text(lang, "premium_info"),
        reply_markup=await premium_keyboard(lang, register_url),
    )
    await callback.answer()


@router.callback_query(F.data == "menu:status")
async def menu_status(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)
    lang = user.language if user else "bn"
    min_dep = await get_min_deposit()

    if not user:
        await _safe_edit(
            callback,
            get_text(lang, "status_title") + get_text(lang, "status_not_verified"),
            reply_markup=await back_keyboard(lang),
        )
        await callback.answer()
        return

    joined = "Yes ✅" if user.has_joined else "No ❌"
    verified = "Yes ✅" if user.is_verified else "No ❌"
    verified_at = user.verified_at.strftime("%Y-%m-%d %H:%M") if user.verified_at else "-"

    text = get_text(lang, "status_title")
    text += get_text(
        lang,
        "status_full",
        trader_id=user.trader_id or "-",
        country=user.country or "-",
        total_deposit=user.total_deposit or 0,
        total_withdraw=user.total_withdraw or 0,
        last_deposit=user.last_deposit or 0,
        min_deposit=int(min_dep),
        verified=verified,
        verified_at=verified_at,
        joined=joined,
    )

    async with async_session() as session:
        q = select(PostbackLog).where(
            or_(
                PostbackLog.trader_id == (user.trader_id or ""),
                PostbackLog.click_id == str(callback.from_user.id),
            )
        ).order_by(PostbackLog.id.desc()).limit(8)
        result = await session.execute(q)
        logs = result.scalars().all()

    if logs:
        text += "\n\n" + get_text(lang, "history_title") + "\n"
        for log in logs:
            when = log.created_at.strftime("%m-%d %H:%M") if log.created_at else "-"
            text += (
                f"• {when} | status=<code>{log.status or '-'}</code> "
                f"dep=${log.sumdep or 0:.2f} "
                f"uid=<code>{log.trader_id or '-'}</code>\n"
            )
    else:
        text += "\n\n" + get_text(lang, "history_empty")

    await _safe_edit(callback, text, reply_markup=await back_keyboard(lang))
    await callback.answer()


@router.callback_query(F.data == "menu:public")
async def menu_public(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)
    lang = user.language if user else "bn"
    channel = await get_setting("public_channel")
    text = get_text(lang, "public_channel")
    if channel:
        text = (
            f"🔗 ফ্রি সিগন্যাল পাবলিক চ্যানেল:\n{channel}"
            if lang == "bn"
            else f"🔗 Free Signal Public Channel:\n{channel}"
        )
    await _safe_edit(callback, text, reply_markup=await back_keyboard(lang))
    await callback.answer()


@router.callback_query(F.data == "menu:support")
async def menu_support(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)
    lang = user.language if user else "bn"
    support = await get_support_text(lang)
    await _safe_edit(callback, support, reply_markup=await back_keyboard(lang))
    await callback.answer()


@router.callback_query(F.data == "menu:create")
async def menu_create(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)
    lang = user.language if user else "bn"
    register_url = await get_affiliate_url(str(callback.from_user.id))
    await _safe_edit(
        callback,
        get_text(lang, "create_account_guide"),
        reply_markup=await premium_keyboard(lang, register_url),
    )
    await callback.answer()


@router.callback_query(F.data == "menu:delete")
async def menu_delete(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)
    lang = user.language if user else "bn"
    await _safe_edit(
        callback,
        get_text(lang, "delete_account_guide"),
        reply_markup=await back_keyboard(lang),
    )
    await callback.answer()
