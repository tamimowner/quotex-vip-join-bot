from aiogram import Router
from aiogram.types import ChatMemberUpdated
from aiogram.filters import ChatMemberUpdatedFilter, IS_NOT_MEMBER, IS_MEMBER
from services.invite import mark_joined_and_revoke
from config import settings

router = Router()


@router.chat_member(
    ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER)
)
async def on_user_joined(event: ChatMemberUpdated):
    """When a user joins the VIP group → mark as joined + revoke their personal link."""
    if event.chat.id != settings.VIP_GROUP_ID:
        return

    user_id = event.new_chat_member.user.id
    await mark_joined_and_revoke(event.bot, user_id)
