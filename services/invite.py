from datetime import datetime
from aiogram import Bot
from sqlalchemy import select
from database.models import User
from database.db import async_session
from services.settings_store import get_vip_group_link
from config import settings


async def create_unique_invite(bot: Bot, telegram_id: int) -> str | None:
    """
    Create a one-time invite link for this user only (member_limit=1).
    Requires VIP_GROUP_ID and bot must be admin in the VIP group/channel.
    Falls back to static VIP_GROUP_LINK from admin panel if API fails.
    """
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        if not user or not user.is_verified:
            return None

        # Reuse existing unused unique link if already stored
        if user.invite_link and user.invite_link_name and user.invite_link_name != "static":
            if not user.has_joined:
                return user.invite_link

        link: str | None = None
        link_name = f"u{telegram_id}"

        chat_id = settings.VIP_GROUP_ID
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
                print(f"create_chat_invite_link failed: {e}")

        if not link:
            # Fallback: static link from admin panel / env
            static = await get_vip_group_link()
            if static:
                link = static
                link_name = "static"

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
