from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    WebAppInfo,
)
from aiogram.enums import MessageEntityType
from aiogram.filters import Command, BaseFilter
from sqlalchemy import select, func
from config import settings
from database.db import async_session
from database.models import User, PostbackLog
from services.settings_store import get_setting, set_setting, get_button_text, get_min_deposit
import os

router = Router()

_pending: dict[int, str] = {}

BUTTON_MAP = [
    ("btn_premium", "VIP জয়েন বাটন"),
    ("btn_create_account", "নতুন অ্যাকাউন্ট বাটন"),
    ("btn_delete_account", "অ্যাকাউন্ট ডিলিট বাটন"),
    ("btn_public", "পাবলিক চ্যানেল বাটন"),
    ("btn_status", "স্ট্যাটাস বাটন"),
    ("btn_support", "সাপোর্ট বাটন"),
    ("btn_register", "রেজিস্টার বাটন"),
    ("btn_back", "ফিরে যান বাটন"),
    ("btn_settings", "সেটিংস বাটন"),
]

STYLE_CHOICES = [
    ("success", "🟢 সবুজ (success)"),
    ("primary", "🔵 নীল (primary)"),
    ("danger", "🔴 লাল (danger)"),
]


def is_admin(user_id: int) -> bool:
    return user_id in settings.admin_ids


def _web_admin_base_url() -> str:
    for key in ("WEB_BASE_URL", "ADMIN_WEB_URL", "PUBLIC_URL", "RAILWAY_PUBLIC_DOMAIN"):
        val = (os.getenv(key) or "").strip().rstrip("/")
        if val:
            if key == "RAILWAY_PUBLIC_DOMAIN" and not val.startswith("http"):
                return f"https://{val}"
            return val
    return ""


def _web_admin_url() -> str:
    """No token in URL — WebApp verifies Telegram user via initData + ADMIN_IDS."""
    base = _web_admin_base_url()
    if not base:
        return ""
    if not base.startswith("https://"):
        if base.startswith("http://"):
            base = "https://" + base[len("http://"):]
        else:
            base = "https://" + base
    return f"{base}/admin"


def admin_choose_kb() -> InlineKeyboardMarkup:
    rows = []
    web_url = _web_admin_url()
    if web_url:
        rows.append([InlineKeyboardButton(text="🌐 Web App খুলুন", web_app=WebAppInfo(url=web_url))])
        rows.append([InlineKeyboardButton(text="ℹ️ Web App info", callback_data="adm:choose:web", style="success")])
    else:
        rows.append([InlineKeyboardButton(text="🌐 Web Panel (URL সেট করুন)", callback_data="adm:choose:web", style="success")])
    rows.append([InlineKeyboardButton(text="⌨️ Command Panel", callback_data="adm:choose:cmd", style="primary")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def admin_menu_kb() -> InlineKeyboardMarkup:
    rows = []
    web_url = _web_admin_url()
    if web_url:
        rows.append([InlineKeyboardButton(text="🌐 Web App খুলুন", web_app=WebAppInfo(url=web_url))])
    rows.extend([
        [InlineKeyboardButton(text="💰 মিনিমাম ডিপোজিট", callback_data="adm:mindep", style="success")],
        [InlineKeyboardButton(text="🖼 ওয়েলকাম ফটো", callback_data="adm:photo", style="success")],
        [InlineKeyboardButton(text="🔗 পার্টনার লিংক", callback_data="adm:link", style="primary")],
        [InlineKeyboardButton(text="📋 সব বাটন", callback_data="adm:map", style="primary")],
        [InlineKeyboardButton(text="💎 বাটন টেক্সট", callback_data="adm:btns", style="success")],
        [InlineKeyboardButton(text="🎨 বাটন কালার", callback_data="adm:styles", style="success")],
        [InlineKeyboardButton(text="✨ প্রিমিয়াম ইমোজি", callback_data="adm:icons", style="success")],
        [InlineKeyboardButton(text="📊 স্ট্যাটস", callback_data="adm:stats", style="primary")],
        [InlineKeyboardButton(text="👥 ইউজার", callback_data="adm:users", style="primary")],
        [InlineKeyboardButton(text="📢 পাবলিক চ্যানেল", callback_data="adm:public", style="primary")],
        [InlineKeyboardButton(text="🆘 সাপোর্ট", callback_data="adm:support", style="primary")],
        [InlineKeyboardButton(text="◀️ প্যানেল বেছে নিন", callback_data="adm:choose", style="primary")],
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)


class AdminPendingFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return bool(message.from_user and message.from_user.id in _pending and is_admin(message.from_user.id))


@router.message(Command("admin"))
async def cmd_admin(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ শুধু অ্যাডমিন (ADMIN_IDS)")
        return
    min_dep = await get_min_deposit()
    web_url = _web_admin_url()
    extra = (
        "\n✅ Web App খুললে টেলিগ্রাম ID দিয়ে অটো লগইন (টোকেন লাগে না)।"
        if web_url
        else "\n⚠️ Railway এ <code>WEB_BASE_URL</code> সেট করুন।"
    )
    await message.answer(
        "🛠 <b>অ্যাডমিন প্যানেল</b>\n\n"
        f"💰 মিনিমাম ডিপোজিট: <b>${min_dep:.0f}</b>\n"
        f"🆔 <code>{message.from_user.id}</code>\n\n"
        "🌐 <b>Web App</b> — পুরো কন্ট্রোল\n"
        "⌨️ <b>Command Panel</b> — চ্যাট মেনু"
        + extra,
        reply_markup=admin_choose_kb(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "adm:choose")
async def adm_choose_again(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Forbidden", show_alert=True)
        return
    await callback.message.edit_text(
        "🛠 <b>অ্যাডমিন প্যানেল</b>\n\nকোন প্যানেল?",
        reply_markup=admin_choose_kb(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "adm:choose:web")
async def adm_choose_web(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Forbidden", show_alert=True)
        return
    web_url = _web_admin_url()
    if web_url:
        text = (
            "🌐 <b>Web Admin</b>\n\n"
            "শুধু <code>ADMIN_IDS</code> এর ইউজার লগইন করতে পারবে।\n"
            "Web App বাটনে চাপলে টেলিগ্রাম অটো ভেরিফাই করবে — <b>টোকেন লাগে না</b>।\n\n"
            f"URL: <code>{web_url}</code>"
        )
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🌐 Web App খুলুন", web_app=WebAppInfo(url=web_url))],
            [InlineKeyboardButton(text="⌨️ Command Panel", callback_data="adm:choose:cmd", style="primary")],
            [InlineKeyboardButton(text="◀️ ফিরে", callback_data="adm:choose", style="primary")],
        ])
    else:
        text = (
            "⚠️ <code>WEB_BASE_URL</code> সেট নেই।\n\n"
            "Railway: <code>WEB_BASE_URL=https://your-app.up.railway.app</code>\n"
            "এবং <code>ADMIN_IDS</code> = আপনার Telegram numeric ID"
        )
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⌨️ Command Panel", callback_data="adm:choose:cmd", style="primary")],
            [InlineKeyboardButton(text="◀️ ফিরে", callback_data="adm:choose", style="primary")],
        ])
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML", disable_web_page_preview=True)
    await callback.answer()


@router.callback_query(F.data == "adm:choose:cmd")
async def adm_choose_cmd(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Forbidden", show_alert=True)
        return
    min_dep = await get_min_deposit()
    await callback.message.edit_text(
        f"⌨️ <b>Command Panel</b>\n\n💰 ${min_dep:.0f}\n🆔 <code>{callback.from_user.id}</code>",
        reply_markup=admin_menu_kb(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "adm:mindep")
async def adm_mindep(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    current = await get_min_deposit()
    _pending[callback.from_user.id] = "min_deposit"
    await callback.message.edit_text(
        f"💰 বর্তমান: <b>${current:.0f}</b>\nনতুন সংখ্যা পাঠান।",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ মেনু", callback_data="adm:home", style="primary")]]),
    )
    await callback.answer()


@router.callback_query(F.data == "adm:photo")
async def adm_photo(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    _pending[callback.from_user.id] = "welcome_photo"
    await callback.message.edit_text(
        "🖼 ছবি পাঠান / URL / <code>clear</code>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ মেনু", callback_data="adm:home", style="primary")]]),
    )
    await callback.answer()


@router.callback_query(F.data == "adm:map")
async def adm_map(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    lines = ["📋 <b>বাটন</b>\n"]
    for key, title in BUTTON_MAP:
        bn = await get_button_text(key, "bn")
        en = await get_button_text(key, "en")
        lines.append(f"<b>{title}</b>\n🇧🇩 <code>{bn}</code>\n🇬🇧 <code>{en}</code>\n")
    await callback.message.edit_text(
        "\n".join(lines),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ মেনু", callback_data="adm:home", style="primary")]]),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "adm:stats")
async def adm_stats(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    async with async_session() as session:
        total = await session.scalar(select(func.count()).select_from(User)) or 0
        verified = await session.scalar(select(func.count()).select_from(User).where(User.is_verified.is_(True))) or 0
        joined = await session.scalar(select(func.count()).select_from(User).where(User.has_joined.is_(True))) or 0
        posts = await session.scalar(select(func.count()).select_from(PostbackLog)) or 0
        deposits = await session.scalar(select(func.coalesce(func.sum(User.total_deposit), 0))) or 0
    min_dep = await get_min_deposit()
    await callback.message.edit_text(
        f"📊 Users: {total} | Verified: {verified} | Joined: {joined}\n"
        f"Postbacks: {posts} | Dep: ${float(deposits):.2f} | Min: ${min_dep:.0f}",
        reply_markup=admin_menu_kb(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "adm:users")
async def adm_users(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    async with async_session() as session:
        result = await session.execute(select(User).order_by(User.id.desc()).limit(10))
        users = result.scalars().all()
    lines = [f"{'✅' if u.is_verified else '⏳'} <code>{u.telegram_id}</code> {u.full_name or '-'} ${u.total_deposit or 0:.2f}" for u in users]
    await callback.message.edit_text("👥\n" + ("\n".join(lines) or "empty"), reply_markup=admin_menu_kb(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "adm:link")
async def adm_link(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    current = await get_setting("affiliate_link_base")
    _pending[callback.from_user.id] = "affiliate_link_base"
    await callback.message.edit_text(f"🔗 <code>{current}</code>\nনতুন লিংক পাঠান:", parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "adm:public")
async def adm_public(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    current = await get_setting("public_channel")
    _pending[callback.from_user.id] = "public_channel"
    await callback.message.edit_text(f"📢 <code>{current}</code>\nনতুন লিংক:", parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "adm:support")
async def adm_support(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    await callback.message.edit_text(
        "🆘 ভাষা?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🇧🇩", callback_data="adm:supportlang:bn", style="success"),
             InlineKeyboardButton(text="🇬🇧", callback_data="adm:supportlang:en", style="primary")],
            [InlineKeyboardButton(text="⬅️", callback_data="adm:home", style="primary")],
        ]),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("adm:supportlang:"))
async def adm_support_lang(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    lang = callback.data.split(":")[-1]
    key = f"support_text_{lang}"
    _pending[callback.from_user.id] = key
    current = await get_setting(key, "")
    await callback.message.edit_text(f"🆘 {lang}:\n{current or 'নেই'}\nনতুন টেক্সট:", parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "adm:btns")
async def adm_btns(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    rows = [[InlineKeyboardButton(text=title, callback_data=f"adm:btnlang:{key}", style="primary")] for key, title in BUTTON_MAP]
    rows.append([InlineKeyboardButton(text="⬅️", callback_data="adm:home", style="primary")])
    await callback.message.edit_text("💎 বাটন সিলেক্ট:", reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))
    await callback.answer()


@router.callback_query(F.data.startswith("adm:btnlang:"))
async def adm_btn_pick_lang(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    key = callback.data.split("adm:btnlang:", 1)[1]
    bn = await get_button_text(key, "bn")
    en = await get_button_text(key, "en")
    await callback.message.edit_text(
        f"<code>{key}</code>\n🇧🇩 {bn}\n🇬🇧 {en}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🇧🇩", callback_data=f"adm:set:{key}_bn", style="success"),
             InlineKeyboardButton(text="🇬🇧", callback_data=f"adm:set:{key}_en", style="primary")],
            [InlineKeyboardButton(text="⬅️", callback_data="adm:btns", style="primary")],
        ]),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "adm:styles")
async def adm_styles(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    rows = [[InlineKeyboardButton(text=title[:40], callback_data=f"adm:stylepick:{key}", style="primary")] for key, title in BUTTON_MAP]
    rows.append([InlineKeyboardButton(text="⬅️", callback_data="adm:home", style="primary")])
    await callback.message.edit_text("🎨", reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))
    await callback.answer()


@router.callback_query(F.data.startswith("adm:stylepick:"))
async def adm_style_pick(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    key = callback.data.split("adm:stylepick:", 1)[1]
    current = await get_setting(f"style_{key}", "primary")
    rows = [[InlineKeyboardButton(text=label + (" ✅" if val == current else ""), callback_data=f"adm:styleset:{key}:{val}", style=val)] for val, label in STYLE_CHOICES]
    rows.append([InlineKeyboardButton(text="⬅️", callback_data="adm:styles", style="primary")])
    await callback.message.edit_text(f"🎨 {key} = {current}", reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))
    await callback.answer()


@router.callback_query(F.data.startswith("adm:styleset:"))
async def adm_style_set(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    parts = callback.data.split(":")
    key, style = parts[2], parts[3]
    await set_setting(f"style_{key}", style)
    await callback.answer(f"✅ {style}", show_alert=True)
    await callback.message.edit_text(f"✅ {key} = {style}", reply_markup=admin_menu_kb())


@router.callback_query(F.data == "adm:icons")
async def adm_icons(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    rows = [[InlineKeyboardButton(text=title[:40], callback_data=f"adm:iconset:{key}", style="success")] for key, title in BUTTON_MAP]
    rows.append([InlineKeyboardButton(text="⬅️", callback_data="adm:home", style="primary")])
    await callback.message.edit_text("✨", reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))
    await callback.answer()


@router.callback_query(F.data.startswith("adm:iconset:"))
async def adm_icon_set(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    key = callback.data.split("adm:iconset:", 1)[1]
    _pending[callback.from_user.id] = f"icon_{key}"
    current = await get_setting(f"icon_{key}", "")
    await callback.message.edit_text(f"✨ {key}\nid: <code>{current or 'নেই'}</code>\nকাস্টম ইমোজি পাঠান / clear", parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "adm:home")
async def adm_home(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    _pending.pop(callback.from_user.id, None)
    await callback.message.edit_text("⌨️ Command Panel", reply_markup=admin_menu_kb())
    await callback.answer()


@router.callback_query(F.data.startswith("adm:set:"))
async def adm_set_key(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    key = callback.data.split("adm:set:", 1)[1]
    _pending[callback.from_user.id] = key
    current = await get_setting(key, "")
    await callback.message.edit_text(f"📝 <code>{key}</code>\n{current or 'নেই'}\nনতুন টেক্সট:", parse_mode="HTML")
    await callback.answer()


@router.message(AdminPendingFilter(), F.photo)
async def admin_photo_input(message: Message):
    if _pending.get(message.from_user.id) != "welcome_photo":
        return
    _pending.pop(message.from_user.id, None)
    await set_setting("welcome_photo_file_id", message.photo[-1].file_id)
    await set_setting("welcome_photo_url", "")
    await message.answer("✅ ফটো সেভ", reply_markup=admin_menu_kb())


@router.message(AdminPendingFilter(), F.text)
async def admin_text_input(message: Message):
    uid = message.from_user.id
    key = _pending.pop(uid)
    value = (message.text or "").strip()

    if key == "min_deposit":
        try:
            amount = float(value.replace("$", "").strip())
            if amount < 0:
                raise ValueError()
        except ValueError:
            _pending[uid] = key
            await message.answer("❌ শুধু সংখ্যা")
            return
        await set_setting("min_deposit", str(amount))
        await message.answer(f"✅ ${amount:.0f}", reply_markup=admin_menu_kb(), parse_mode="HTML")
        return

    if key == "welcome_photo":
        if value.lower() == "clear":
            await set_setting("welcome_photo_url", "")
            await set_setting("welcome_photo_file_id", "")
            await message.answer("✅ মুছেছে", reply_markup=admin_menu_kb())
            return
        if value.startswith("http"):
            await set_setting("welcome_photo_url", value)
            await set_setting("welcome_photo_file_id", "")
            await message.answer("✅ URL", reply_markup=admin_menu_kb())
            return
        _pending[uid] = key
        await message.answer("❌ URL বা ছবি")
        return

    if key.startswith("icon_"):
        if value.lower() == "clear":
            await set_setting(key, "")
            await message.answer("✅", reply_markup=admin_menu_kb())
            return
        emoji_id = None
        if message.entities:
            for ent in message.entities:
                if ent.type == MessageEntityType.CUSTOM_EMOJI and ent.custom_emoji_id:
                    emoji_id = str(ent.custom_emoji_id)
                    break
        if not emoji_id and value.isdigit() and len(value) >= 10:
            emoji_id = value
        if not emoji_id:
            _pending[uid] = key
            await message.answer("❌ কাস্টম ইমোজি দরকার")
            return
        await set_setting(key, emoji_id)
        await message.answer(f"✅ <code>{emoji_id}</code>", reply_markup=admin_menu_kb(), parse_mode="HTML")
        return

    await set_setting(key, value)
    await message.answer(f"✅ <code>{key}</code>", reply_markup=admin_menu_kb(), parse_mode="HTML")
