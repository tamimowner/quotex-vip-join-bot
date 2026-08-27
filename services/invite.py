from datetime import datetime
from aiogram import Bot
from sqlalchemy import select
from database.models import User
from database.db import async_session
from services.settings_store import get_vip_group_link


async def get_static_invite_link() -> str | None:
    """Return the same static VIP group link for every verified user (PHP style)."""
    link = await get_vip_group_link()
    return link if link else None


async def create_unique_invite(bot: Bot, telegram_id: int) -> str | None:
    """
    Compatibility wrapper.
    Now returns the static VIP group link instead of creating member_limit=1 links.
    """
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        if not user or not user.is_verified:
            return None

        link = await get_static_invite_link()
        if not link:
            return None

        # Store static link on user so menu/status can show it
        if user.invite_link != link:
            user.invite_link = link
            user.invite_link_name = "static"
            await session.commit()

        return link


async def mark_joined_and_revoke(bot: Bot, telegram_id: int):
    """Mark user as joined. No revoke needed for static link."""
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
