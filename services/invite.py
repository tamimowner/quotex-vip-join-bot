from datetime import datetime
from aiogram import Bot
from sqlalchemy import select
from database.models import User
from database.db import async_session
from services.settings_store import get_vip_group_link, get_setting
from config import settings

# New VIP group/channel (super group form)
DEFAULT_VIP_GROUP_ID = -1003931217242


async def get_vip_chat_id() -> int:
    """DB setting vip_group_id → env VIP_GROUP_ID → default new group."""
    raw = await get_setting("vip_group_id", "")
    if raw:
        try:
            return int(str(raw).strip())
        except (TypeError, ValueError):
            pass
    if settings.VIP_GROUP_ID:
        return int(settings.VIP_GROUP_ID)
    return DEFAULT_VIP_GROUP_ID


async def create_unique_invite(bot: Bot, telegram_id: int) -> str | None:
    """
    Always create a fresh one-time invite for the CURRENT VIP group.
    Does NOT reuse old invite links (so group change takes effect).
    Requires bot to be admin in the VIP group/channel.
    """
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        if not user or not user.is_verified:
            return None

        link: str | None = None
        link_name = f"u{telegram_id}"

        chat_id = await get_vip_chat_id()
        print(f"create_unique_invite: using VIP chat_id={chat_id} for user={telegram_id}")

        if chat_id:
            try:
                invite = await bot.create_chat_invite_link(
                    chat_id=chat_id,
                    name=link_name[:32],
                    member_limit=1,
                    creates_join_request=False,
                )
                link = invite.invite_link
            except Exception as e:
                print(f"create_chat_invite_link failed for {chat_id}: {e}")

        if not link:
            # Fallback: static link from admin panel / env
            static = await get_vip_group_link()
            if static:
                link = static
                link_name = "static"
                print(f"Using static VIP link fallback: {static}")

        if not link:
            return None

        user.invite_link = link
        user.invite_link_name = link_name
        await session.commit()
        return link


async def mark_joined_and_revoke(bot: Bot, telegram_id: int):
    """Mark user as joined when they enter VIP group."""
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        if not user or user.has_joined:
            return

        user.has_joined = True
        user.joined_at = datetime.utcnow()
        await session.commit()
