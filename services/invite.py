from datetime import datetime
from aiogram import Bot
from aiogram.types import ChatInviteLink
from sqlalchemy import select
from database.models import User
from database.db import async_session
from config import settings
from locales import get_text


async def create_unique_invite(bot: Bot, telegram_id: int) -> str | None:
    """
    Create a unique invite link with member_limit=1 for the user.
    Only that user can join. After join we will revoke it.
    """
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        if not user or not user.is_verified:
            return None

        if user.invite_link and not user.has_joined:
            return user.invite_link

        try:
            # Create one-time invite link (member_limit=1)
            link: ChatInviteLink = await bot.create_chat_invite_link(
                chat_id=settings.VIP_GROUP_ID,
                name=f"user_{telegram_id}",
                member_limit=1,
                creates_join_request=False,
            )

            user.invite_link = link.invite_link
            user.invite_link_name = link.name
            await session.commit()

            return link.invite_link
        except Exception as e:
            print(f"Error creating invite link: {e}")
            return None


async def mark_joined_and_revoke(bot: Bot, telegram_id: int):
    """Mark user as joined and revoke their personal invite link."""
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        if not user or user.has_joined:
            return

        user.has_joined = True
        user.joined_at = datetime.utcnow()

        # Revoke the invite link if exists
        if user.invite_link_name:
            try:
                await bot.revoke_chat_invite_link(
                    chat_id=settings.VIP_GROUP_ID,
                    invite_link=user.invite_link
                )
            except Exception as e:
                print(f"Error revoking link: {e}")

        user.invite_link = None
        await session.commit()
