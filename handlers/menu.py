from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy import select
from database.models import User
from database.db import async_session
from keyboards import main_menu, premium_keyboard, back_keyboard
from locales import get_text
from config import settings
from services.invite import create_unique_invite

router = Router()


async def get_user(telegram_id: int) -> User | None:
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()


@router.callback_query(F.data == "menu:back")
async def menu_back(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)
    lang = user.language if user else "bn"
    name = callback.from_user.first_name or "User"
    await callback.message.edit_text(
        get_text(lang, "welcome", name=name),
        reply_markup=main_menu(lang),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "menu:premium")
async def menu_premium(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)
    lang = user.language if user else "bn"

    if user and user.is_verified and user.invite_link and not user.has_joined:
        await callback.message.edit_text(
            get_text(lang, "invite_ready", link=user.invite_link),
            reply_markup=back_keyboard(lang),
            parse_mode="HTML",
            disable_web_page_preview=True
        )
        await callback.answer()
        return

    if user and user.has_joined:
        await callback.message.edit_text(
            get_text(lang, "already_joined"),
            reply_markup=back_keyboard(lang),
            parse_mode="HTML"
        )
        await callback.answer()
        return

    # Build affiliate link with click_id = telegram_id
    click_id = str(callback.from_user.id)
    register_url = settings.AFFILIATE_LINK_BASE.format(
        click_id=click_id,
        site_id=settings.SITE_ID
    )

    await callback.message.edit_text(
        get_text(lang, "premium_info"),
        reply_markup=premium_keyboard(lang, register_url),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "menu:status")
async def menu_status(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)
    lang = user.language if user else "bn"

    if not user or not user.is_verified:
        text = get_text(lang, "status_title") + get_text(lang, "status_not_verified")
    else:
        joined = "Yes ✅" if user.has_joined else "No ❌"
        verified_at = user.verified_at.strftime("%Y-%m-%d %H:%M") if user.verified_at else "-"
        text = get_text(lang, "status_title") + get_text(
            lang, "status_verified",
            trader_id=user.trader_id or "-",
            country=user.country or "-",
            total_deposit=user.total_deposit or 0,
            total_withdraw=user.total_withdraw or 0,
            last_deposit=user.last_deposit or 0,
            verified_at=verified_at,
            joined=joined
        )

    await callback.message.edit_text(
        text,
        reply_markup=back_keyboard(lang),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "menu:public")
async def menu_public(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)
    lang = user.language if user else "bn"
    await callback.message.edit_text(
        get_text(lang, "public_channel"),
        reply_markup=back_keyboard(lang),
        parse_mode="HTML",
        disable_web_page_preview=True
    )
    await callback.answer()


@router.callback_query(F.data == "menu:support")
async def menu_support(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)
    lang = user.language if user else "bn"
    await callback.message.edit_text(
        get_text(lang, "support"),
        reply_markup=back_keyboard(lang),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "menu:create")
async def menu_create(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)
    lang = user.language if user else "bn"
    await callback.message.edit_text(
        get_text(lang, "create_account_guide"),
        reply_markup=back_keyboard(lang),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "menu:delete")
async def menu_delete(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)
    lang = user.language if user else "bn"
    await callback.message.edit_text(
        get_text(lang, "delete_account_guide"),
        reply_markup=back_keyboard(lang),
        parse_mode="HTML"
    )
    await callback.answer()
