from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from sqlalchemy import select, func
from config import settings
from database.db import async_session
from database.models import User, PostbackLog
from services.settings_store import get_setting, set_setting, DEFAULTS

router = Router()

# Simple in-memory wait state for admin text input
_pending: dict[int, str] = {}


def is_admin(user_id: int) -> bool:
    return user_id in settings.admin_ids


def admin_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔗 কোটেক্স পার্টনার লিংক", callback_data="adm:link")],
        [InlineKeyboardButton(text="💎 বাটন ইমোজি/টেক্সট", callback_data="adm:btns")],
        [InlineKeyboardButton(text="📊 স্ট্যাটস", callback_data="adm:stats")],
        [InlineKeyboardButton(text="👥 ইউজার লিস্ট (শেষ ১০)", callback_data="adm:users")],
        [InlineKeyboardButton(text="📢 পাবলিক চ্যানেল লিংক", callback_data="adm:public")],
        [InlineKeyboardButton(text="🆘 সাপোর্ট টেক্সট", callback_data="adm:support")],
    ])


@router.message(Command("admin"))
async def cmd_admin(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ শুধু অ্যাডমিন ব্যবহার করতে পারবে।")
        return
    await message.answer(
        "🛠 <b>অ্যাডমিন প্যানেল</b>\n\n"
        "এখান থেকে কোটেক্স লিংক, বাটন ইমোজি ও সেটিংস ম্যানেজ করুন।\n\n"
        f"আপনার ID: <code>{message.from_user.id}</code>",
        reply_markup=admin_menu_kb(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "adm:stats")
async def adm_stats(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Forbidden", show_alert=True)
        return
    async with async_session() as session:
        total = await session.scalar(select(func.count()).select_from(User)) or 0
        verified = await session.scalar(
            select(func.count()).select_from(User).where(User.is_verified == True)  # noqa: E712
        ) or 0
        joined = await session.scalar(
            select(func.count()).select_from(User).where(User.has_joined == True)  # noqa: E712
        ) or 0
        posts = await session.scalar(select(func.count()).select_from(PostbackLog)) or 0
        deposits = await session.scalar(select(func.coalesce(func.sum(User.total_deposit), 0))) or 0

    await callback.message.edit_text(
        f"📊 <b>স্ট্যাটস</b>\n\n"
        f"👥 মোট ইউজার: <b>{total}</b>\n"
        f"✅ ভেরিফাইড: <b>{verified}</b>\n"
        f"🎟 VIP জয়েন: <b>{joined}</b>\n"
        f"📥 Postback লগ: <b>{posts}</b>\n"
        f"💰 মোট ডিপোজিট (ট্র্যাকড): <b>${float(deposits):.2f}</b>",
        reply_markup=admin_menu_kb(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "adm:users")
async def adm_users(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Forbidden", show_alert=True)
        return
    async with async_session() as session:
        result = await session.execute(
            select(User).order_by(User.id.desc()).limit(10)
        )
        users = result.scalars().all()

    lines = []
    for u in users:
        flag = "✅" if u.is_verified else "⏳"
        lines.append(
            f"{flag} <code>{u.telegram_id}</code> "
            f"{u.full_name or '-'} | dep=${u.total_deposit or 0:.2f}"
        )
    text = "👥 <b>শেষ ১০ ইউজার</b>\n\n" + ("\n".join(lines) if lines else "কোনো ইউজার নেই")
    await callback.message.edit_text(text, reply_markup=admin_menu_kb(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "adm:link")
async def adm_link(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Forbidden", show_alert=True)
        return
    current = await get_setting("affiliate_link_base")
    _pending[callback.from_user.id] = "affiliate_link_base"
    await callback.message.edit_text(
        f"🔗 <b>বর্তমান কোটেক্স পার্টনার লিংক</b>\n\n"
        f"<code>{current}</code>\n\n"
        f"নতুন লিংক পাঠান।\n"
        f"উদাহরণ:\n"
        f"<code>https://broker-qx.pro/sign-up/?lid=1480996&click_id={{click_id}}&site_id={{site_id}}</code>\n\n"
        f"⚠️ <code>{{click_id}}</code> ও <code>{{site_id}}</code> রাখুন যাতে ট্র্যাকিং কাজ করে।",
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "adm:public")
async def adm_public(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    current = await get_setting("public_channel")
    _pending[callback.from_user.id] = "public_channel"
    await callback.message.edit_text(
        f"📢 বর্তমান পাবলিক চ্যানেল:\n<code>{current}</code>\n\nনতুন লিংক পাঠান:",
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "adm:support")
async def adm_support(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    current = await get_setting("support_text")
    _pending[callback.from_user.id] = "support_text"
    await callback.message.edit_text(
        f"🆘 বর্তমান সাপোর্ট টেক্সট:\n{current}\n\nনতুন টেক্সট পাঠান:",
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "adm:btns")
async def adm_btns(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="btn_premium", callback_data="adm:set:btn_premium")],
        [InlineKeyboardButton(text="btn_register", callback_data="adm:set:btn_register")],
        [InlineKeyboardButton(text="btn_status", callback_data="adm:set:btn_status")],
        [InlineKeyboardButton(text="btn_public", callback_data="adm:set:btn_public")],
        [InlineKeyboardButton(text="btn_support", callback_data="adm:set:btn_support")],
        [InlineKeyboardButton(text="btn_create_account", callback_data="adm:set:btn_create_account")],
        [InlineKeyboardButton(text="btn_delete_account", callback_data="adm:set:btn_delete_account")],
        [InlineKeyboardButton(text="⬅️ অ্যাডমিন মেনু", callback_data="adm:home")],
    ])
    await callback.message.edit_text(
        "💎 <b>বাটন টেক্সট / ইমোজি সেট</b>\n\n"
        "যে বাটন বদলাতে চান সিলেক্ট করুন, তারপর নতুন টেক্সট + ইমোজি পাঠান।\n"
        "উদাহরণ: <code>💎 প্রিমিয়াম VIP জয়েন</code>",
        reply_markup=kb,
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "adm:home")
async def adm_home(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    await callback.message.edit_text(
        "🛠 <b>অ্যাডমিন প্যানেল</b>",
        reply_markup=admin_menu_kb(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("adm:set:"))
async def adm_set_key(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    key = callback.data.split("adm:set:", 1)[1]
    current = await get_setting(key)
    _pending[callback.from_user.id] = key
    await callback.message.edit_text(
        f"বর্তমান (<code>{key}</code>):\n<code>{current}</code>\n\nনতুন টেক্সট পাঠান (ইমোজিসহ):",
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(F.text)
async def admin_text_input(message: Message):
    """Capture admin pending input. Must be registered carefully — only if pending."""
    uid = message.from_user.id
    if uid not in _pending:
        return
    if not is_admin(uid):
        _pending.pop(uid, None)
        return

    key = _pending.pop(uid)
    value = message.text.strip()
    await set_setting(key, value)
    await message.answer(
        f"✅ সেভ হয়েছে\n<code>{key}</code> =\n{value}",
        reply_markup=admin_menu_kb(),
        parse_mode="HTML",
    )
