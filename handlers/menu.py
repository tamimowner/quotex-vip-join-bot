from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, MessageEntity
from sqlalchemy import select
from database.models import User, PostbackLog
from database.db import async_session
from keyboards import (
    main_menu,
    premium_keyboard,
    back_keyboard,
    settings_keyboard,
    settings_language_keyboard,
)
from services.settings_store import (
    get_affiliate_url,
    get_setting,
    get_support_text,
    get_min_deposit,
    get_vip_group_link,
)
from handlers.start import get_bot_display_name
from services.messages import get_message_text
from config import settings

router = Router()


async def get_user(telegram_id: int) -> User | None:
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()


async def _safe_edit(
    callback: CallbackQuery,
    text: str,
    reply_markup=None,
    entities: list[MessageEntity] | None = None,
):
    """
    Edit current message; photo → edit_caption; else new message.
    If entities given: no parse_mode (custom emoji via entities).
    Otherwise use HTML parse_mode (works reliably for tg-emoji on this bot).
    """
    text = (text or "")[:4000]
    msg = callback.message
    use_entities = bool(entities)

    # Prefer new message for entity-based custom emoji (most reliable)
    if use_entities:
        try:
            await msg.answer(
                text,
                reply_markup=reply_markup,
                entities=entities,
                disable_web_page_preview=True,
            )
            return
        except Exception as e:
            print(f"_safe_edit entities answer: {e}")

    try:
        kwargs = dict(
            reply_markup=reply_markup,
            disable_web_page_preview=True,
        )
        if use_entities:
            kwargs["entities"] = entities
        else:
            kwargs["parse_mode"] = "HTML"
        await msg.edit_text(text, **kwargs)
        return
    except Exception as e:
        print(f"_safe_edit edit_text: {e}")

    try:
        kwargs = dict(reply_markup=reply_markup)
        if use_entities:
            kwargs["caption_entities"] = entities
        else:
            kwargs["parse_mode"] = "HTML"
        await msg.edit_caption(caption=text, **kwargs)
        return
    except Exception as e:
        print(f"_safe_edit edit_caption: {e}")

    try:
        kwargs = dict(
            reply_markup=reply_markup,
            disable_web_page_preview=True,
        )
        if use_entities:
            kwargs["entities"] = entities
        else:
            kwargs["parse_mode"] = "HTML"
        await msg.answer(text, **kwargs)
        return
    except Exception as e:
        print(f"_safe_edit answer: {e}")

    try:
        plain = (
            text.replace("<b>", "")
            .replace("</b>", "")
            .replace("<code>", "")
            .replace("</code>", "")
        )
        while "<tg-emoji" in plain:
            start = plain.find("<tg-emoji")
            end = plain.find(">", start)
            if end == -1:
                break
            plain = plain[:start] + plain[end + 1 :]
        plain = plain.replace("</tg-emoji>", "")
        await msg.answer(plain[:4000], reply_markup=reply_markup)
    except Exception as e:
        print(f"_safe_edit plain: {e}")


@router.callback_query(F.data == "menu:back")
async def menu_back(callback: CallbackQuery, bot: Bot):
    try:
        user = await get_user(callback.from_user.id)
        lang = user.language if user else "bn"
        bot_name = await get_bot_display_name(bot)
        register_url = await get_affiliate_url()
        text = await get_message_text(
            lang,
            "welcome",
            botName=bot_name,
            register_url=register_url,
        )
        await _safe_edit(callback, text, reply_markup=await main_menu(lang))
    except Exception as e:
        print(f"menu_back error: {e}")
    await callback.answer()


@router.callback_query(F.data == "menu:settings")
async def menu_settings(callback: CallbackQuery):
    try:
        user = await get_user(callback.from_user.id)
        lang = user.language if user else "bn"
        await _safe_edit(
            callback,
            await get_message_text(lang, "settings_title"),
            reply_markup=await settings_keyboard(lang),
        )
    except Exception as e:
        print(f"menu_settings error: {e}")
    await callback.answer()


@router.callback_query(F.data == "settings:lang")
async def settings_lang(callback: CallbackQuery):
    try:
        user = await get_user(callback.from_user.id)
        lang = user.language if user else "bn"
        await _safe_edit(
            callback,
            await get_message_text(lang, "choose_language"),
            reply_markup=await settings_language_keyboard(lang),
        )
    except Exception as e:
        print(f"settings_lang error: {e}")
    await callback.answer()


@router.callback_query(F.data == "menu:premium")
async def menu_premium(callback: CallbackQuery):
    try:
        user = await get_user(callback.from_user.id)
        lang = user.language if user else "bn"

        if user and user.is_verified:
            vip_link = user.invite_link or await get_vip_group_link()
            if vip_link:
                await _safe_edit(
                    callback,
                    await get_message_text(
                        lang,
                        "invite_ready",
                        link=vip_link,
                        trader_id=user.trader_id or "-",
                    ),
                    reply_markup=None,
                )
                await callback.answer()
                return

        if user and user.has_joined:
            await _safe_edit(
                callback,
                await get_message_text(lang, "already_joined"),
                reply_markup=await back_keyboard(lang),
            )
            await callback.answer()
            return

        register_url = await get_affiliate_url()
        await _safe_edit(
            callback,
            await get_message_text(lang, "premium_info"),
            reply_markup=await premium_keyboard(lang, register_url),
        )
    except Exception as e:
        print(f"menu_premium error: {e}")
    await callback.answer()


@router.callback_query(F.data == "menu:status")
async def menu_status(callback: CallbackQuery):
    try:
        user = await get_user(callback.from_user.id)
        lang = user.language if user else "bn"
        min_dep = await get_min_deposit()

        if not user or not user.is_verified:
            title = await get_message_text(lang, "status_title")
            body = await get_message_text(lang, "status_not_verified")
            await _safe_edit(
                callback,
                title + body,
                reply_markup=await back_keyboard(lang),
            )
            await callback.answer()
            return

        joined = "Yes" if user.has_joined else "No"
        verified = "Yes"
        verified_at = (
            user.verified_at.strftime("%Y-%m-%d %H:%M") if user.verified_at else "-"
        )

        text = await get_message_text(lang, "status_title")
        text += await get_message_text(
            lang,
            "status_full",
            trader_id=user.trader_id or "-",
            country=user.country or "-",
            total_deposit=float(user.total_deposit or 0),
            total_withdraw=float(user.total_withdraw or 0),
            last_deposit=float(user.last_deposit or 0),
            min_deposit=int(min_dep),
            verified=verified,
            verified_at=verified_at,
            joined=joined,
        )

        # Postback history: ONLY for admins
        is_admin = callback.from_user.id in settings.admin_ids
        if is_admin:
            async with async_session() as session:
                q = (
                    select(PostbackLog)
                    .where(PostbackLog.trader_id == (user.trader_id or ""))
                    .order_by(PostbackLog.id.desc())
                    .limit(8)
                )
                result = await session.execute(q)
                logs = result.scalars().all()

            if logs:
                text += "\n\n" + await get_message_text(lang, "history_title") + "\n"
                for log in logs:
                    when = log.created_at.strftime("%m-%d %H:%M") if log.created_at else "-"
                    text += (
                        f"• {when} | status=<code>{log.status or '-'}</code> "
                        f"dep=${float(log.sumdep or 0):.2f} "
                        f"uid=<code>{log.trader_id or '-'}</code>\n"
                    )
            else:
                text += "\n\n" + await get_message_text(lang, "history_empty")

        await _safe_edit(callback, text, reply_markup=await back_keyboard(lang))
    except Exception as e:
        print(f"menu_status error: {e}")
    await callback.answer()


@router.callback_query(F.data == "menu:public")
async def menu_public(callback: CallbackQuery):
    try:
        user = await get_user(callback.from_user.id)
        lang = user.language if user else "bn"
        text = await get_message_text(lang, "public_channel")
        await _safe_edit(callback, text, reply_markup=await back_keyboard(lang))
    except Exception as e:
        print(f"menu_public error: {e}")
    await callback.answer()


@router.callback_query(F.data == "menu:support")
async def menu_support(callback: CallbackQuery):
    try:
        user = await get_user(callback.from_user.id)
        lang = user.language if user else "bn"

        # Prefer locale HTML version (with custom emoji)
        # Only use DB override if it contains tg-emoji (so custom emoji still work)
        support = await get_message_text(lang, "support")
        msg_ov = await get_setting(f"msg_support_{lang}", "")
        if msg_ov and "<tg-emoji" in msg_ov:
            support = msg_ov
        else:
            custom = await get_support_text(lang)
            if custom and "<tg-emoji" in custom:
                support = custom

        # Always send NEW message with HTML so custom emoji work reliably
        await callback.message.answer(
            support,
            reply_markup=await back_keyboard(lang),
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
    except Exception as e:
        print(f"menu_support error: {e}")
    await callback.answer()


@router.callback_query(F.data == "menu:create")
async def menu_create(callback: CallbackQuery):
    try:
        user = await get_user(callback.from_user.id)
        lang = (user.language if user else None) or "bn"
        register_url = await get_affiliate_url()
        text = await get_message_text(
            lang,
            "create_account_guide",
            register_url=register_url or "",
        )
        kb = await premium_keyboard(lang, register_url)
        # Always send NEW message with HTML so custom emoji + bold work reliably
        await callback.message.answer(
            text,
            reply_markup=kb,
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
    except Exception as e:
        print(f"menu_create error: {e}")
        try:
            await callback.message.answer(
                f"Create account guide error. Please /start again.\n<code>{e}</code>",
                parse_mode="HTML",
            )
        except Exception:
            pass
    await callback.answer()


@router.callback_query(F.data == "menu:delete")
async def menu_delete(callback: CallbackQuery):
    try:
        user = await get_user(callback.from_user.id)
        lang = (user.language if user else None) or "bn"
        text = await get_message_text(lang, "delete_account_guide")
        # Always send NEW message with HTML so custom emoji + bold work reliably
        await callback.message.answer(
            text,
            reply_markup=await back_keyboard(lang),
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
    except Exception as e:
        print(f"menu_delete error: {e}")
        try:
            await callback.message.answer(
                f"Delete guide error. Please /start again.\n<code>{e}</code>",
                parse_mode="HTML",
            )
        except Exception:
            pass
    await callback.answer()
