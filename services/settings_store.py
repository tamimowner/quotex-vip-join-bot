from sqlalchemy import select
from database.db import async_session
from database.models import BotSettings
from config import settings as env_settings

DEFAULTS = {
    "affiliate_link_base": env_settings.AFFILIATE_LINK_BASE,
    "site_id": env_settings.SITE_ID,
    "btn_premium": "💎 প্রিমিয়াম VIP জয়েন প্রক্রিয়া",
    "btn_create_account": "⭐ নতুন কোটেক্স অ্যাকাউন্ট তৈরি",
    "btn_delete_account": "🗑 পুরাতন অ্যাকাউন্ট ডিলিট গাইড",
    "btn_public": "📢 ফ্রি সিগন্যাল পাবলিক চ্যানেল",
    "btn_status": "📊 আমার অ্যাকাউন্ট স্ট্যাটাস",
    "btn_support": "🆘 সাপোর্ট / হেল্প",
    "btn_register": "🚀 কোটেক্সে রেজিস্টার ও ডিপোজিট",
    "btn_back": "⬅️ ফিরে যান",
    "public_channel": "https://t.me/+gLV8BLij6PAxYjE1",
    "support_text": "কোনো সমস্যা হলে অ্যাডমিন: @TEADMIN9",
    # Welcome media
    "welcome_photo_url": "",
    "welcome_photo_file_id": "",
}


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


async def get_affiliate_url(click_id: str) -> str:
    base = await get_setting("affiliate_link_base")
    site_id = await get_setting("site_id")
    if "{click_id}" not in base:
        sep = "&" if "?" in base else "?"
        base = f"{base}{sep}click_id={{click_id}}"
    if "{site_id}" not in base:
        base = f"{base}&site_id={{site_id}}"
    try:
        return base.format(click_id=click_id, site_id=site_id)
    except Exception:
        return base.replace("{click_id}", click_id).replace("{site_id}", site_id)
