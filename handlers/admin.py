from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.enums import MessageEntityType
from aiogram.filters import Command, BaseFilter
from sqlalchemy import select, func, desc
from config import settings
from database.db import async_session
from database.models import User, PostbackLog
from services.settings_store import (
    get_setting,
    set_setting,
    get_button_text,
    get_min_deposit,
    get_affiliate_url,
    get_vip_group_link,
)

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
    ("btn_open_account", "Quotex Account খুলুন বাটন"),
    ("btn_tutorial", "Tutorial বাটন"),
    ("btn_back", "ফিরে যান বাটন"),
    ("btn_settings", "সেটিংস বাটন"),
]

STYLE_CHOICES = [
    ("success", "সবুজ (success)"),
    ("primary", "নীল (primary)"),
    ("danger", "লাল (danger)"),
]


def is_admin(user_id: int) -> bool:
    return user_id in settings.admin_ids


def admin_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="মিনিমাম ডিপোজিট", callback_data="adm:mindep")],
            [InlineKeyboardButton(text="পার্টনার লিংক", callback_data="adm:link")],
            [InlineKeyboardButton(text="VIP ইনভাইট লিংক", callback_data="adm:vip")],
            [InlineKeyboardButton(text="Tutorial (YouTube)", callback_data="adm:tutorial")],
            [InlineKeyboardButton(text="ওয়েলকাম ফটো", callback_data="adm:photo")],
            [InlineKeyboardButton(text="বাটন টেক্সট", callback_data="adm:btns")],
            [InlineKeyboardButton(text="বাটন কালার", callback_data="adm:styles")],
            [InlineKeyboardButton(text="প্রিমিয়াম ইমোজি", callback_data="adm:icons")],
            [InlineKeyboardButton(text="সব বাটন দেখুন", callback_data="adm:map")],
            [InlineKeyboardButton(text="স্ট্যাটস", callback_data="adm:stats")],
            [InlineKeyboardButton(text="পোস্টব্যাক লগ", callback_data="adm:postbacks")],
            [InlineKeyboardButton(text="ইউজার", callback_data="adm:users")],
            [InlineKeyboardButton(text="পাবলিক চ্যানেল", callback_data="adm:public")],
            [InlineKeyboardButton(text="সাপোর্ট টেক্সট", callback_data="adm:support")],
        ]
    )


def back_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="মেনু", callback_data="adm:home")]
        ]
    )


class AdminPendingFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return bool(
            message.from_user
            and message.from_user.id in _pending
            and is_admin(message.from_user.id)
        )


@router.message(Command("admin"))
async def cmd_admin(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("শুধু অ্যাডমিন (ADMIN_IDS)")
        return
    min_dep = await get_min_deposit()
    aff = await get_affiliate_url()
    await message.answer(
        "<b>অ্যাডমিন কমান্ড প্যানেল</b>\n\n"
        f"মিনিমাম ডিপোজিট: <b>${min_dep:.0f}</b>\n"
        f"পার্টনার: <code>{aff}</code>\n"
        f"আপনার ID: <code>{message.from_user.id}</code>\n\n"
        "নিচের মেনু থেকে সেটিংস পরিবর্তন করুন।",
        reply_markup=admin_menu_kb(),
        parse_mode="HTML",
        disable_web_page_preview=True,
    )


@router.callback_query(F.data == "adm:home")
async def adm_home(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    _pending.pop(callback.from_user.id, None)
    min_dep = await get_min_deposit()
    await callback.message.edit_text(
        f"<b>কমান্ড প্যানেল</b>\nমিনিমাম: ${min_dep:.0f}",
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
        f"বর্তমান: <b>${current:.0f}</b>\nনতুন সংখ্যা পাঠান (0 = শুধু রেজিস্ট্রেশনে ভেরিফাই)।",
        parse_mode="HTML",
        reply_markup=back_kb(),
    )
    await callback.answer()


@router.callback_query(F.data == "adm:photo")
async def adm_photo(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    _pending[callback.from_user.id] = "welcome_photo"
    await callback.message.edit_text(
        "ছবি পাঠান / URL / <code>clear</code>",
        parse_mode="HTML",
        reply_markup=back_kb(),
    )
    await callback.answer()


@router.callback_query(F.data == "adm:link")
async def adm_link(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    current = await get_affiliate_url()
    _pending[callback.from_user.id] = "affiliate_link_base"
    await callback.message.edit_text(
        f"বর্তমান পার্টনার লিংক:\n<code>{current}</code>\n\n"
        "নতুন স্ট্যাটিক লিংক পাঠান\n"
        "উদাহরণ: <code>https://broker-qx.pro/sign-up/?lid=1480996</code>",
        parse_mode="HTML",
        reply_markup=back_kb(),
        disable_web_page_preview=True,
    )
    await callback.answer()


@router.callback_query(F.data == "adm:vip")
async def adm_vip(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    current = await get_vip_group_link()
    _pending[callback.from_user.id] = "vip_group_link"
    await callback.message.edit_text(
        f"VIP invite:\n<code>{current or 'সেট নেই'}</code>\n\nনতুন লিংক পাঠান:",
        parse_mode="HTML",
        reply_markup=back_kb(),
        disable_web_page_preview=True,
    )
    await callback.answer()


@router.callback_query(F.data == "adm:tutorial")
async def adm_tutorial(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    current = await get_setting("tutorial_url", "")
    _pending[callback.from_user.id] = "tutorial_url"
    await callback.message.edit_text(
        f"Tutorial / YouTube লিংক:\n<code>{current or 'সেট নেই'}</code>\n\n"
        "নতুন YouTube URL পাঠান:\n"
        "উদাহরণ: <code>https://youtu.be/xxxxx</code>",
        parse_mode="HTML",
        reply_markup=back_kb(),
        disable_web_page_preview=True,
    )
    await callback.answer()


@router.callback_query(F.data == "adm:map")
async def adm_map(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    lines = ["<b>বাটন ম্যাপ</b>\n"]
    for key, title in BUTTON_MAP:
        bn = await get_button_text(key, "bn")
        en = await get_button_text(key, "en")
        lines.append(f"<b>{title}</b>\nBN <code>{bn}</code>\nEN <code>{en}</code>\n")
    await callback.message.edit_text(
        "\n".join(lines)[:4000],
        reply_markup=back_kb(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "adm:stats")
async def adm_stats(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    async with async_session() as session:
        total = await session.scalar(select(func.count()).select_from(User)) or 0
        verified = (
            await session.scalar(
                select(func.count()).select_from(User).where(User.is_verified.is_(True))
            )
            or 0
        )
        joined = (
            await session.scalar(
                select(func.count()).select_from(User).where(User.has_joined.is_(True))
            )
            or 0
        )
        posts = await session.scalar(select(func.count()).select_from(PostbackLog)) or 0
        deposits = (
            await session.scalar(
                select(func.coalesce(func.sum(User.total_deposit), 0))
            )
            or 0
        )
    min_dep = await get_min_deposit()
    await callback.message.edit_text(
        f"<b>স্ট্যাটস</b>\n"
        f"Users: {total}\nVerified: {verified}\nJoined: {joined}\n"
        f"Postbacks: {posts}\nTotal dep: ${float(deposits):.2f}\nMin: ${min_dep:.0f}",
        reply_markup=admin_menu_kb(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "adm:postbacks")
async def adm_postbacks(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    async with async_session() as session:
        result = await session.execute(
            select(PostbackLog).order_by(desc(PostbackLog.id)).limit(15)
        )
        rows = result.scalars().all()
    if not rows:
        text = (
            "<b>পোস্টব্যাক লগ খালি</b>\n\n"
            "চেক:\n"
            "1) Quotex Partner URL:\n"
            "<code>...railway.app/postback?status={status}&uid={trader_id}&...</code>\n"
            "2) টেস্ট:\n"
            "<code>/postback?status=reg&uid=TEST1&sumdep=0</code>\n"
            "3) Railway Logs এ POSTBACK hit দেখুন"
        )
    else:
        lines = ["<b>শেষ ১৫ পোস্টব্যাক</b>\n"]
        for r in rows:
            t = (r.created_at.isoformat() if r.created_at else "-")[:19]
            lines.append(
                f"{t} | {r.status or '-'} | uid={r.trader_id or '-'} | "
                f"${float(r.sumdep or 0):.2f}"
            )
        text = "\n".join(lines)
    await callback.message.edit_text(
        text[:4000],
        reply_markup=admin_menu_kb(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "adm:users")
async def adm_users(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    async with async_session() as session:
        result = await session.execute(select(User).order_by(User.id.desc()).limit(12))
        users = result.scalars().all()
    lines = []
    for u in users:
        mark = "OK" if u.is_verified else ".."
        lines.append(
            f"{mark} <code>{u.telegram_id}</code> "
            f"{u.full_name or '-'} tid={u.trader_id or '-'} "
            f"${float(u.total_deposit or 0):.2f}"
        )
    await callback.message.edit_text(
        "<b>ইউজার</b>\n" + ("\n".join(lines) or "empty"),
        reply_markup=admin_menu_kb(),
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
        f"<code>{current}</code>\nনতুন লিংক:",
        parse_mode="HTML",
        reply_markup=back_kb(),
    )
    await callback.answer()


@router.callback_query(F.data == "adm:support")
async def adm_support(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    await callback.message.edit_text(
        "সাপোর্ট টেক্সট — ভাষা?",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="BN", callback_data="adm:supportlang:bn"),
                    InlineKeyboardButton(text="EN", callback_data="adm:supportlang:en"),
                ],
                [InlineKeyboardButton(text="মেনু", callback_data="adm:home")],
            ]
        ),
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
    await callback.message.edit_text(
        f"{lang}:\n{current or 'নেই'}\nনতুন টেক্সট:",
        parse_mode="HTML",
        reply_markup=back_kb(),
    )
    await callback.answer()


@router.callback_query(F.data == "adm:btns")
async def adm_btns(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    rows = [
        [InlineKeyboardButton(text=title, callback_data=f"adm:btnlang:{key}")]
        for key, title in BUTTON_MAP
    ]
    rows.append([InlineKeyboardButton(text="মেনু", callback_data="adm:home")])
    await callback.message.edit_text(
        "বাটন সিলেক্ট:", reply_markup=InlineKeyboardMarkup(inline_keyboard=rows)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("adm:btnlang:"))
async def adm_btn_pick_lang(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    key = callback.data.split("adm:btnlang:", 1)[1]
    bn = await get_button_text(key, "bn")
    en = await get_button_text(key, "en")
    await callback.message.edit_text(
        f"<code>{key}</code>\nBN {bn}\nEN {en}",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="BN", callback_data=f"adm:set:{key}_bn"),
                    InlineKeyboardButton(text="EN", callback_data=f"adm:set:{key}_en"),
                ],
                [InlineKeyboardButton(text="ফিরে", callback_data="adm:btns")],
            ]
        ),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "adm:styles")
async def adm_styles(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    rows = [
        [InlineKeyboardButton(text=title[:40], callback_data=f"adm:stylepick:{key}")]
        for key, title in BUTTON_MAP
    ]
    rows.append([InlineKeyboardButton(text="মেনু", callback_data="adm:home")])
    await callback.message.edit_text(
        "বাটন কালার:", reply_markup=InlineKeyboardMarkup(inline_keyboard=rows)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("adm:stylepick:"))
async def adm_style_pick(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    key = callback.data.split("adm:stylepick:", 1)[1]
    current = await get_setting(f"style_{key}", "primary")
    rows = [
        [
            InlineKeyboardButton(
                text=label + (" *" if val == current else ""),
                callback_data=f"adm:styleset:{key}:{val}",
            )
        ]
        for val, label in STYLE_CHOICES
    ]
    rows.append([InlineKeyboardButton(text="ফিরে", callback_data="adm:styles")])
    await callback.message.edit_text(
        f"{key} = {current}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("adm:styleset:"))
async def adm_style_set(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    parts = callback.data.split(":")
    key, style = parts[2], parts[3]
    await set_setting(f"style_{key}", style)
    await callback.answer(f"OK {style}", show_alert=True)
    await callback.message.edit_text(
        f"{key} = {style}", reply_markup=admin_menu_kb()
    )


@router.callback_query(F.data == "adm:icons")
async def adm_icons(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    rows = [
        [InlineKeyboardButton(text=title[:40], callback_data=f"adm:iconset:{key}")]
        for key, title in BUTTON_MAP
    ]
    rows.append([InlineKeyboardButton(text="মেনু", callback_data="adm:home")])
    await callback.message.edit_text(
        "প্রিমিয়াম ইমোজি:", reply_markup=InlineKeyboardMarkup(inline_keyboard=rows)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("adm:iconset:"))
async def adm_icon_set(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    key = callback.data.split("adm:iconset:", 1)[1]
    _pending[callback.from_user.id] = f"icon_{key}"
    current = await get_setting(f"icon_{key}", "")
    await callback.message.edit_text(
        f"{key}\nid: <code>{current or 'নেই'}</code>\nকাস্টম ইমোজি পাঠান / clear",
        parse_mode="HTML",
        reply_markup=back_kb(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("adm:set:"))
async def adm_set_key(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    key = callback.data.split("adm:set:", 1)[1]
    _pending[callback.from_user.id] = key
    current = await get_setting(key, "")
    await callback.message.edit_text(
        f"<code>{key}</code>\n{current or 'নেই'}\nনতুন টেক্সট:",
        parse_mode="HTML",
        reply_markup=back_kb(),
    )
    await callback.answer()


@router.message(AdminPendingFilter(), F.photo)
async def admin_photo_input(message: Message):
    if _pending.get(message.from_user.id) != "welcome_photo":
        return
    _pending.pop(message.from_user.id, None)
    await set_setting("welcome_photo_file_id", message.photo[-1].file_id)
    await set_setting("welcome_photo_url", "")
    await message.answer("ফটো সেভ হয়েছে", reply_markup=admin_menu_kb())


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
            await message.answer("শুধু সংখ্যা পাঠান")
            return
        await set_setting("min_deposit", str(amount))
        await message.answer(
            f"মিনিমাম ডিপোজিট ${amount:.0f}",
            reply_markup=admin_menu_kb(),
            parse_mode="HTML",
        )
        return

    if key == "welcome_photo":
        if value.lower() == "clear":
            await set_setting("welcome_photo_url", "")
            await set_setting("welcome_photo_file_id", "")
            await message.answer("মুছেছে", reply_markup=admin_menu_kb())
            return
        if value.startswith("http"):
            await set_setting("welcome_photo_url", value)
            await set_setting("welcome_photo_file_id", "")
            await message.answer("URL সেভ", reply_markup=admin_menu_kb())
            return
        _pending[uid] = key
        await message.answer("URL বা ছবি পাঠান")
        return

    if key == "tutorial_url":
        if not value.startswith("http"):
            _pending[uid] = key
            await message.answer("পূর্ণ URL পাঠান (https://...)")
            return
        await set_setting("tutorial_url", value)
        await message.answer(
            f"Tutorial সেভ:\n<code>{value}</code>",
            reply_markup=admin_menu_kb(),
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
        return

    if key.startswith("icon_"):
        if value.lower() == "clear":
            await set_setting(key, "")
            await message.answer("ক্লিয়ার", reply_markup=admin_menu_kb())
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
            await message.answer("কাস্টম ইমোজি দরকার")
            return
        await set_setting(key, emoji_id)
        await message.answer(
            f"সেভ <code>{emoji_id}</code>",
            reply_markup=admin_menu_kb(),
            parse_mode="HTML",
        )
        return

    await set_setting(key, value)
    await message.answer(
        f"সেভ <code>{key}</code>",
        reply_markup=admin_menu_kb(),
        parse_mode="HTML",
    )
