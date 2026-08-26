from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import MessageEntityType
from aiogram.filters import Command, BaseFilter
from sqlalchemy import select, func
from config import settings
from database.db import async_session
from database.models import User, PostbackLog
from services.settings_store import get_setting, set_setting

router = Router()

_pending: dict[int, str] = {}

# Human-readable map for admin
BUTTON_MAP = [
    ("btn_premium", "প্রিমিয়াম VIP জয়েন বাটন (মেইন মেনু)"),
    ("btn_create_account", "নতুন অ্যাকাউন্ট গাইড বাটন"),
    ("btn_delete_account", "পুরাতন অ্যাকাউন্ট ডিলিট বাটন"),
    ("btn_public", "পাবলিক চ্যানেল বাটন"),
    ("btn_status", "অ্যাকাউন্ট স্ট্যাটাস বাটন"),
    ("btn_support", "সাপোর্ট বাটন"),
    ("btn_register", "কোটেক্স রেজিস্টার URL বাটন"),
    ("btn_back", "ফিরে যান বাটন"),
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
        [InlineKeyboardButton(text="🔗 কোটেক্স পার্টনার লিংক", callback_data="adm:link", style="primary")],
        [InlineKeyboardButton(text="📋 সব বাটন টেক্সট দেখুন", callback_data="adm:map", style="primary")],
        [InlineKeyboardButton(text="💎 বাটন টেক্সট/ইমোজি", callback_data="adm:btns", style="success")],
        [InlineKeyboardButton(text="🎨 বাটন কালার (style)", callback_data="adm:styles", style="success")],
        [InlineKeyboardButton(text="✨ প্রিমিয়াম ইমোজি আইকন", callback_data="adm:icons", style="success")],
        [InlineKeyboardButton(text="📊 স্ট্যাটস", callback_data="adm:stats", style="primary")],
        [InlineKeyboardButton(text="👥 ইউজার লিস্ট", callback_data="adm:users", style="primary")],
        [InlineKeyboardButton(text="📢 পাবলিক চ্যানেল", callback_data="adm:public", style="primary")],
        [InlineKeyboardButton(text="🆘 সাপোর্ট টেক্সট", callback_data="adm:support", style="primary")],
    ])


@router.message(Command("admin"))
async def cmd_admin(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ শুধু অ্যাডমিন ব্যবহার করতে পারবে।")
        return
    await message.answer(
        "🛠 <b>অ্যাডমিন প্যানেল</b>\n\n"
        "• বাটন টেক্সট + ইউনিকোড ইমোজি\n"
        "• বাটন কালার: 🟢 success / 🔵 primary / 🔴 danger\n"
        "• প্রিমিয়াম কাস্টম ইমোজি (Telegram Premium প্রয়োজন)\n\n"
        f"আপনার ID: <code>{message.from_user.id}</code>\n\n"
        "⚠️ প্রিমিয়াম ইমোজি দেখাতে <b>বট ওনার অ্যাকাউন্টে Telegram Premium</b> থাকতে হবে।",
        reply_markup=admin_menu_kb(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "adm:map")
async def adm_map(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    lines = ["📋 <b>সব বাটন — পুরো টেক্সট ম্যাপ</b>\n"]
    for key, title in BUTTON_MAP:
        text = await get_setting(key)
        style = await get_setting(f"style_{key}", "-")
        icon = await get_setting(f"icon_{key}", "")
        lines.append(
            f"<b>{title}</b>\n"
            f"Key: <code>{key}</code>\n"
            f"Text: <code>{text}</code>\n"
            f"Color: <code>{style}</code>\n"
            f"Premium emoji id: <code>{icon or 'নেই'}</code>\n"
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
        f"বর্তমান:\n<code>{current}</code>\n\n"
        f"নতুন ডিরেক্ট Quotex লিংক পাঠান:\n"
        f"<code>https://broker-qx.pro/sign-up/?lid=1480996&click_id={{click_id}}&site_id={{site_id}}</code>",
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
    current = await get_setting("support_text")
    _pending[callback.from_user.id] = "support_text"
    await callback.message.edit_text(
        f"🆘 বর্তমান:\n{current}\n\nনতুন সাপোর্ট টেক্সট পাঠান:",
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "adm:btns")
async def adm_btns(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    rows = []
    for key, title in BUTTON_MAP:
        current = await get_setting(key)
        short = (current[:28] + "…") if len(current) > 28 else current
        rows.append([InlineKeyboardButton(
            text=f"{short}",
            callback_data=f"adm:set:{key}",
            style="primary",
        )])
    rows.append([InlineKeyboardButton(text="⬅️ অ্যাডমিন মেনু", callback_data="adm:home", style="primary")])
    await callback.message.edit_text(
        "💎 <b>বাটন টেক্সট সেট</b>\n\n"
        "বাটন সিলেক্ট করুন → নতুন টেক্সট পাঠান (সাধারণ ইমোজিসহ)।\n"
        "প্রিমিয়াম কাস্টম ইমোজির জন্য আলাদা মেনু: <b>প্রিমিয়াম ইমোজি আইকন</b>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows),
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
        "🎨 <b>বাটন কালার</b>\n\n"
        "🟢 success = সবুজ\n🔵 primary = নীল\n🔴 danger = লাল\n\n"
        "যে বাটনের কালার বদলাবেন সিলেক্ট করুন:",
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
        f"🎨 <code>{key}</code>\nবর্তমান: <b>{current}</b>\n\nনতুন কালার বাছুন:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("adm:styleset:"))
async def adm_style_set(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    # adm:styleset:btn_premium:success
    parts = callback.data.split(":")
    # ['adm', 'styleset', 'btn_premium', 'success']
    key = parts[2]
    style = parts[3]
    await set_setting(f"style_{key}", style)
    await callback.answer(f"✅ {key} → {style}", show_alert=True)
    await callback.message.edit_text(
        f"✅ সেভ: <code>{key}</code> কালার = <b>{style}</b>\n\n/start দিয়ে মেনু দেখুন।",
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
        "✨ <b>প্রিমিয়াম কাস্টম ইমোজি</b>\n\n"
        "১) নিচ থেকে বাটন সিলেক্ট করুন\n"
        "২) Telegram Premium কাস্টম ইমোজি পাঠান (শুধু ইমোজি বা ইমোজি+টেক্সট)\n"
        "৩) বট <code>custom_emoji_id</code> সেভ করবে\n\n"
        "⚠️ বট ওনারের অ্যাকাউন্টে <b>Telegram Premium</b> থাকতে হবে, নাহলে ইমোজি দেখাবে না।",
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
        f"✨ <code>{key}</code> এর প্রিমিয়াম ইমোজি\n\n"
        f"বর্তমান id: <code>{current or 'নেই'}</code>\n\n"
        f"এখন <b>কাস্টম/প্রিমিয়াম ইমোজি</b> পাঠান।\n"
        f"মুছে ফেলতে: <code>clear</code> লিখুন।",
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
    title = next((t for k, t in BUTTON_MAP if k == key), key)
    _pending[callback.from_user.id] = key
    await callback.message.edit_text(
        f"📝 <b>{title}</b>\n"
        f"Key: <code>{key}</code>\n\n"
        f"বর্তমান পুরো টেক্সট:\n<code>{current}</code>\n\n"
        f"নতুন টেক্সট পাঠান (সাধারণ ইমোজি 👍⭐💎 চলবে):",
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(AdminPendingFilter(), F.text)
async def admin_text_input(message: Message):
    uid = message.from_user.id
    key = _pending.pop(uid)
    value = (message.text or "").strip()

    # Premium custom emoji capture for icon_* keys
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
            # allow pasting raw id
            if value.isdigit() and len(value) >= 10:
                emoji_id = value
            else:
                _pending[uid] = key
                await message.answer(
                    "❌ কাস্টম ইমোজি পাওয়া যায়নি।\n"
                    "Telegram Premium কাস্টম ইমোজি পাঠান, অথবা emoji id নম্বর পাঠান।"
                )
                return
        await set_setting(key, emoji_id)
        await message.answer(
            f"✅ প্রিমিয়াম ইমোজি সেভ\n<code>{key}</code> = <code>{emoji_id}</code>\n\n"
            f"/start দিয়ে বাটন চেক করুন।",
            reply_markup=admin_menu_kb(),
            parse_mode="HTML",
        )
        return

    await set_setting(key, value)
    await message.answer(
        f"✅ সেভ হয়েছে\n<code>{key}</code> =\n{value}",
        reply_markup=admin_menu_kb(),
        parse_mode="HTML",
    )
