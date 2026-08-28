from sqlalchemy import select
from database.db import async_session
from database.models import BotSettings
from config import settings as env_settings
from locales import get_text
import re

DEFAULTS = {
    "affiliate_link_base": env_settings.AFFILIATE_LINK_BASE
    or "https://broker-qx.pro/sign-up/?lid=1480996",
    "site_id": env_settings.SITE_ID,
    "min_deposit": "0",
    "vip_group_link": env_settings.VIP_GROUP_LINK or "",
    "btn_premium": "VIP জয়েন",
    "btn_create_account": "নতুন অ্যাকাউন্ট",
    "btn_delete_account": "অ্যাকাউন্ট ডিলিট",
    "btn_public": "পাবলিক চ্যানেল",
    "btn_status": "স্ট্যাটাস",
    "btn_support": "সাপোর্ট",
    "btn_register": "রেজিস্টার",
    "btn_back": "ফিরে যান",
    "btn_settings": "সেটিংস",
    "public_channel": "https://t.me/+gLV8BLij6PAxYjE1",
    "support_text": "কোনো সমস্যা হলে অ্যাডমিন: @TEADMIN9",
    "support_text_bn": "কোনো সমস্যা হলে অ্যাডমিন: @TEADMIN9",
    "support_text_en": "Any problem? Contact admin: @TEADMIN9",
    "welcome_photo_url": "",
    "welcome_photo_file_id": "",
}

BUTTON_KEYS = [
    "btn_premium",
    "btn_create_account",
    "btn_delete_account",
    "btn_public",
    "btn_status",
    "btn_support",
    "btn_register",
    "btn_back",
    "btn_settings",
]


async def get_setting(key: str, default: str | None = None) -> str:
    async with async_session() as session:
        result = await session.execute(
            select(BotSettings).where(BotSettings.key == key)
        )
        row = result.scalar_one_or_none()
        if row and row.value is not None and row.value != "":
            return row.value
    if default is not None:
        return default
    return DEFAULTS.get(key, "")


async def set_setting(key: str, value: str) -> None:
    async with async_session() as session:
        result = await session.execute(
            select(BotSettings).where(BotSettings.key == key)
        )
        row = result.scalar_one_or_none()
        if row:
            row.value = value
        else:
            session.add(BotSettings(key=key, value=value))
        await session.commit()


async def get_min_deposit() -> float:
    raw = await get_setting("min_deposit", "0")
    try:
        return float(raw)
    except (TypeError, ValueError):
        return 0.0


async def get_vip_group_link() -> str:
    link = await get_setting("vip_group_link", "")
    if link:
        return link.strip()
    return (env_settings.VIP_GROUP_LINK or "").strip()


async def get_button_text(key: str, lang: str) -> str:
    lang = (lang or "bn").lower()
    if lang not in ("bn", "en"):
        lang = "bn"

    specific = await get_setting(f"{key}_{lang}", "")
    if specific:
        return specific

    locale_val = get_text(lang, key)
    if locale_val and locale_val != key:
        return locale_val

    legacy = await get_setting(key, "")
    if legacy:
        return legacy

    return DEFAULTS.get(key, key)


async def get_support_text(lang: str) -> str:
    lang = (lang or "bn").lower()
    specific = await get_setting(f"support_text_{lang}", "")
    if specific:
        return specific
    legacy = await get_setting("support_text", "")
    if legacy:
        return legacy
    return get_text(lang, "support")


async def get_affiliate_url(click_id: str = "") -> str:
    """সবার জন্য একই স্ট্যাটিক partner লিংক (click_id ব্যবহার হয় না)।"""
    base = (await get_setting("affiliate_link_base") or "").strip()
    if not base:
        base = DEFAULTS["affiliate_link_base"]
    site_id = (await get_setting("site_id") or "1").strip()

    base = base.replace("{click_id}", "").replace("{CLICK_ID}", "")
    base = re.sub(r"([?&])click_id=[^&]*", r"\1", base, flags=re.I)
    base = re.sub(r"[?&]$", "", base)
    base = base.replace("?&", "?").replace("&&", "&")

    if "{site_id}" in base:
        try:
            base = base.format(site_id=site_id)
        except Exception:
            base = base.replace("{site_id}", site_id)

    return base.rstrip("?&")
