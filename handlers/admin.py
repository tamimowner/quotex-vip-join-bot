from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import MessageEntityType
from aiogram.filters import Command, BaseFilter
from sqlalchemy import select, func
from config import settings
from database.db import async_session
from database.models import User, PostbackLog
from services.settings_store import get_setting, set_setting, get_button_text

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


class AdminPendingFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return bool(
            message.from_user
            and message.from_user.id in _pending
            and is_admin(message.from_user.id)
        )


def admin_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🖼 ওয়েলকাম ফটো (URL/আপলোড)", callback_data="adm:photo", style="success")],
        [InlineKeyboardButton(text="🔗 কোটেক্স পার্টনার লিংক", callback_data="adm:link", style="primary")],
        [InlineKeyboardButton(text="📋 সব বাটন টেক্সট দেখুন", callback_data="adm:map", style="primary")],
        [InlineKeyboardButton(text="💎 বাটন টেক্সট (BN/EN)", callback_data="adm:btns", style="success")],
        [InlineKeyboardButton(text="🎨 বাটন কালার (style)", callback_data="adm:styles", style="success")],
        [InlineKeyboardButton(text="✨ প্রিমিয়াম ইমোজি আইকন", callback_data="adm:icons", style="success")],
        [InlineKeyboardButton(text="📊 স্ট্যাটস", callback_data="adm:stats", style="primary")],
        [InlineKeyboardButton(text="👥 ইউজার লিস্ট", callback_data="adm:users", style="primary")],
        [InlineKeyboardButton(text="📢 পাবলিক চ্যানেল", callback_data="adm:public", style="primary")],
        [InlineKeyboardButton(text="🆘 সাপোর্ট টেক্সট (BN/EN)", callback_data="adm:support", style="primary")],
    ])


@router.message(Command("admin"))
async def cmd_admin(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ শুধু অ্যাডমিন ব্যবহার করতে পারবে।")
        return
    await message.answer(
        "🛠 <b>অ্যাডমিন প্যানেল</b>\n\n"
        "• বাটন টেক্সট <b>আলাদা করে BN + EN</b> সেট করুন\n"
        "• ইউজার যে ভাষা সিলেক্ট করবে, সেই ভাষার বাটন দেখাবে\n"
        "• ওয়েলকাম ফটো, কালার, প্রিমিয়াম ইমোজি\n\n"
        f"আপনার ID: <code>{message.from_user.id}</code>",
        reply_markup=admin_menu_kb(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "adm:photo")
async def adm_photo(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    url = await get_setting("welcome_photo_url", "")
    file_id = await get_setting("welcome_photo_file_id", "")
    _pending[callback.from_user.id] = "welcome_photo"
    await callback.message.edit_text(
        "🖼 <b>ওয়েলকাম ফটো সেট</b>\n\n"
        f"URL: <code>{url or 'নেই'}</code>\n"
        f"file_id: <code>{(file_id[:40] + '…') if file_id and len(file_id) > 40 else (file_id or 'নেই')}</code>\n\n"
        "ছবি পাঠান, অথবা https URL, অথবা <code>clear</code>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ অ্যাডমিন মেনু", callback_data="adm:home", style="primary")],
        ]),
    )
    await callback.answer()


@router.callback_query(F.data == "adm:map")
async def adm_map(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    lines = ["📋 <b>সব বাটন (BN / EN)</b>\n"]
    for key, title in BUTTON_MAP:
        bn = await get_button_text(key, "bn")
        en = await get_button_text(key, "en")
        style = await get_setting(f"style_{key}", "-")
        icon = await get_setting(f"icon_{key}", "")
        lines.append(
            f"<b>{title}</b> (<code>{key}</code>)\n"
            f"🇧🇩 <code>{bn}</code>\n"
            f"🇬🇧 <code>{en}</code>\n"
            f"Color: <code>{style}</code> | emoji: <code>{icon or 'নেই'}</code>\n"
        )
    await callback.message.edit_text(
        "\n".join(lines),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ অ্যাডমিন মেনু", callback_data="adm:home", style="primary")]
        ]),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "adm:stats")
async def adm_stats(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Forbidden", show_alert=True)
        return
    async with async_session() as session:
        total = await session.scalar(select(func.count()).select_from(User)) or 0
        verified = await session.scalar(
            select(func.count()).select_from(User).where(User.is_verified.is_(True))
        ) or 0
        joined = await session.scalar(
            select(func.count()).select_from(User).where(User.has_joined.is_(True))
        ) or 0
        posts = await session.scalar(select(func.count()).select_from(PostbackLog)) or 0
        deposits = await session.scalar(select(func.coalesce(func.sum(User.total_deposit), 0))) or 0

    await callback.message.edit_text(
        f"📊 <b>স্ট্যাটস</b>\n\n"
        f"👥 মোট ইউজার: <b>{total}</b>\n"
        f"✅ ভেরিফাইড: <b>{verified}</b>\n"
        f"🎟 VIP জয়েন: <b>{joined}</b>\n"
        f"📥 Postback লগ: <b>{posts}</b>\n"
        f"💰 মোট ডিপোজিট: <b>${float(deposits):.2f}</b>",
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
    lines = []
    for u in users:
        flag = "✅" if u.is_verified else "⏳"
        lines.append(f"{flag} <code>{u.telegram_id}</code> {u.full_name or '-'} | ${u.total_deposit or 0:.2f}")
    text = "👥 <b>শেষ ১০ ইউজার</b>\n\n" + ("\n".join(lines) if lines else "কোনো ইউজার নেই")
    await callback.message.edit_text(text, reply_markup=admin_menu_kb(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "adm:link")
async def adm_link(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    current = await get_setting("affiliate_link_base")
    _pending[callback.from_user.id] = "affiliate_link_base"
    await callback.message.edit_text(
        f"🔗 <b>কোটেক্স পার্টনার লিংক</b>\n\n"
        f"বর্তমান:\n<code>{current}</code>\n\nনতুন লিংক পাঠান:",
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
        f"📢 বর্তমান:\n<code>{current}</code>\n\nনতুন পাবলিক চ্যানেল লিংক পাঠান:",
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "adm:support")
async def adm_support(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    await callback.message.edit_text(
        "🆘 <b>সাপোর্ট টেক্সট</b>\n\nকোন ভাষার টেক্সট সেট করবেন?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🇧🇩 বাংলা", callback_data="adm:supportlang:bn", style="success"),
                InlineKeyboardButton(text="🇬🇧 English", callback_data="adm:supportlang:en", style="primary"),
            ],
            [InlineKeyboardButton(text="⬅️ অ্যাডমিন মেনু", callback_data="adm:home", style="primary")],
        ]),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("adm:supportlang:"))
async def adm_support_lang(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    lang = callback.data.split(":")[-1]
    key = f"support_text_{lang}"
    current = await get_setting(key, "")
    _pending[callback.from_user.id] = key
    await callback.message.edit_text(
        f"🆘 সাপোর্ট টেক্সট (<b>{lang.upper()}</b>)\n\n"
        f"বর্তমান:\n{current or 'নেই'}\n\nনতুন টেক্সট পাঠান:",
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "adm:btns")
async def adm_btns(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    rows = []
    for key, title in BUTTON_MAP:
        rows.append([InlineKeyboardButton(
            text=title,
            callback_data=f"adm:btnlang:{key}",
            style="primary",
        )])
    rows.append([InlineKeyboardButton(text="⬅️ অ্যাডমিন মেনু", callback_data="adm:home", style="primary")])
    await callback.message.edit_text(
        "💎 <b>বাটন টেক্সট (ভাষা অনুযায়ী)</b>\n\n"
        "১) বাটন সিলেক্ট করুন\n"
        "২) 🇧🇩 বা 🇬🇧 বেছে নিন\n"
        "৩) সেই ভাষার টেক্সট পাঠান\n\n"
        "ইউজার যে ভাষা সিলেক্ট করবে, সেই টেক্সট দেখাবে।",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("adm:btnlang:"))
async def adm_btn_pick_lang(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    key = callback.data.split("adm:btnlang:", 1)[1]
    title = next((t for k, t in BUTTON_MAP if k == key), key)
    bn = await get_button_text(key, "bn")
    en = await get_button_text(key, "en")
    await callback.message.edit_text(
        f"📝 <b>{title}</b>\n<code>{key}</code>\n\n"
        f"🇧🇩 এখন: <code>{bn}</code>\n"
        f"🇬🇧 এখন: <code>{en}</code>\n\n"
        f"কোন ভাষার টেক্সট সেট করবেন?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🇧🇩 বাংলা সেট", callback_data=f"adm:set:{key}_bn", style="success"),
                InlineKeyboardButton(text="🇬🇧 English সেট", callback_data=f"adm:set:{key}_en", style="primary"),
            ],
            [InlineKeyboardButton(text="⬅️ ফিরে", callback_data="adm:btns", style="primary")],
        ]),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "adm:styles")
async def adm_styles(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    rows = []
    for key, title in BUTTON_MAP:
        rows.append([InlineKeyboardButton(
            text=title[:40],
            callback_data=f"adm:stylepick:{key}",
            style="primary",
        )])
    rows.append([InlineKeyboardButton(text="⬅️ অ্যাডমিন মেনু", callback_data="adm:home", style="primary")])
    await callback.message.edit_text(
        "🎨 <b>বাটন কালার</b>\n\n🟢 success / 🔵 primary / 🔴 danger",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("adm:stylepick:"))
async def adm_style_pick(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    key = callback.data.split("adm:stylepick:", 1)[1]
    current = await get_setting(f"style_{key}", "primary")
    rows = [
        [InlineKeyboardButton(
            text=label + (" ✅" if val == current else ""),
            callback_data=f"adm:styleset:{key}:{val}",
            style=val,
        )]
        for val, label in STYLE_CHOICES
    ]
    rows.append([InlineKeyboardButton(text="⬅️ ফিরে", callback_data="adm:styles", style="primary")])
    await callback.message.edit_text(
        f"🎨 <code>{key}</code>\nবর্তমান: <b>{current}</b>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("adm:styleset:"))
async def adm_style_set(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    parts = callback.data.split(":")
    key = parts[2]
    style = parts[3]
    await set_setting(f"style_{key}", style)
    await callback.answer(f"✅ {key} → {style}", show_alert=True)
    await callback.message.edit_text(
        f"✅ সেভ: <code>{key}</code> = <b>{style}</b>",
        reply_markup=admin_menu_kb(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "adm:icons")
async def adm_icons(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    rows = []
    for key, title in BUTTON_MAP:
        rows.append([InlineKeyboardButton(
            text=title[:40],
            callback_data=f"adm:iconset:{key}",
            style="success",
        )])
    rows.append([InlineKeyboardButton(text="⬅️ অ্যাডমিন মেনু", callback_data="adm:home", style="primary")])
    await callback.message.edit_text(
        "✨ <b>প্রিমিয়াম কাস্টম ইমোজি</b>\n\nবাটন সিলেক্ট → কাস্টম ইমোজি পাঠান।",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("adm:iconset:"))
async def adm_icon_set(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    key = callback.data.split("adm:iconset:", 1)[1]
    current = await get_setting(f"icon_{key}", "")
    _pending[callback.from_user.id] = f"icon_{key}"
    await callback.message.edit_text(
        f"✨ <code>{key}</code>\nবর্তমান id: <code>{current or 'নেই'}</code>\n\n"
        f"কাস্টম ইমোজি পাঠান। মুছতে: <code>clear</code>",
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "adm:home")
async def adm_home(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    _pending.pop(callback.from_user.id, None)
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
    current = await get_setting(key, "")
    lang_hint = ""
    if key.endswith("_bn"):
        lang_hint = "🇧🇩 বাংলা"
    elif key.endswith("_en"):
        lang_hint = "🇬🇧 English"
    _pending[callback.from_user.id] = key
    await callback.message.edit_text(
        f"📝 সেট করুন {lang_hint}\nKey: <code>{key}</code>\n\n"
        f"বর্তমান:\n<code>{current or 'নেই'}</code>\n\n"
        f"নতুন টেক্সট পাঠান (ইমোজিসহ চলবে):",
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(AdminPendingFilter(), F.photo)
async def admin_photo_input(message: Message):
    uid = message.from_user.id
    key = _pending.get(uid)
    if key != "welcome_photo":
        return
    _pending.pop(uid, None)
    photo = message.photo[-1]
    await set_setting("welcome_photo_file_id", photo.file_id)
    await set_setting("welcome_photo_url", "")
    await message.answer(
        "✅ ওয়েলকাম ফটো সেভ হয়েছে।\n/start দিয়ে চেক করুন।",
        reply_markup=admin_menu_kb(),
    )


@router.message(AdminPendingFilter(), F.text)
async def admin_text_input(message: Message):
    uid = message.from_user.id
    key = _pending.pop(uid)
    value = (message.text or "").strip()

    if key == "welcome_photo":
        if value.lower() == "clear":
            await set_setting("welcome_photo_url", "")
            await set_setting("welcome_photo_file_id", "")
            await message.answer("✅ ওয়েলকাম ফটো মুছে ফেলা হয়েছে।", reply_markup=admin_menu_kb())
            return
        if value.startswith("http://") or value.startswith("https://"):
            await set_setting("welcome_photo_url", value)
            await set_setting("welcome_photo_file_id", "")
            await message.answer(
                f"✅ ফটো URL সেভ:\n<code>{value}</code>",
                reply_markup=admin_menu_kb(),
                parse_mode="HTML",
            )
            return
        _pending[uid] = key
        await message.answer("❌ URL বা ছবি দরকার। মুছতে: clear")
        return

    if key.startswith("icon_"):
        if value.lower() == "clear":
            await set_setting(key, "")
            await message.answer("✅ প্রিমিয়াম ইমোজি মুছে ফেলা হয়েছে।", reply_markup=admin_menu_kb())
            return
        emoji_id = None
        if message.entities:
            for ent in message.entities:
                if ent.type == MessageEntityType.CUSTOM_EMOJI and ent.custom_emoji_id:
                    emoji_id = str(ent.custom_emoji_id)
                    break
        if not emoji_id:
            if value.isdigit() and len(value) >= 10:
                emoji_id = value
            else:
                _pending[uid] = key
                await message.answer("❌ কাস্টম ইমোজি পাওয়া যায়নি।")
                return
        await set_setting(key, emoji_id)
        await message.answer(
            f"✅ <code>{key}</code> = <code>{emoji_id}</code>",
            reply_markup=admin_menu_kb(),
            parse_mode="HTML",
        )
        return

    await set_setting(key, value)
    await message.answer(
        f"✅ সেভ\n<code>{key}</code> =\n{value}\n\n"
        f"ইউজার ওই ভাষা সিলেক্ট করলে এই টেক্সট দেখাবে।",
        reply_markup=admin_menu_kb(),
        parse_mode="HTML",
    )
