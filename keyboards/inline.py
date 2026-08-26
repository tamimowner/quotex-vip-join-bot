from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from locales import get_text
from services.settings_store import get_setting


def language_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇬🇧 English", callback_data="lang:en", style="primary"),
            InlineKeyboardButton(text="🇧🇩 বাংলা", callback_data="lang:bn", style="success"),
        ]
    ])


async def _btn(
    text: str,
    *,
    callback_data: str | None = None,
    url: str | None = None,
    style: str | None = None,
    icon_custom_emoji_id: str | None = None,
) -> InlineKeyboardButton:
    kwargs: dict = {"text": text}
    if callback_data:
        kwargs["callback_data"] = callback_data
    if url:
        kwargs["url"] = url
    if style in ("primary", "success", "danger"):
        kwargs["style"] = style
    if icon_custom_emoji_id:
        kwargs["icon_custom_emoji_id"] = icon_custom_emoji_id
    return InlineKeyboardButton(**kwargs)


async def main_menu(lang: str) -> InlineKeyboardMarkup:
    # Pair buttons side-by-side (2 per row)
    items = [
        ("btn_premium", "menu:premium", "success"),
        ("btn_status", "menu:status", "primary"),
        ("btn_create_account", "menu:create", "primary"),
        ("btn_delete_account", "menu:delete", "danger"),
        ("btn_public", "menu:public", "primary"),
        ("btn_support", "menu:support", "primary"),
    ]

    built = []
    for key, cb, default_style in items:
        text = await get_setting(key, get_text(lang, key))
        # Short labels look better in 2-column layout
        if len(text) > 28:
            text = text[:26] + "…"
        style = await get_setting(f"style_{key}", default_style)
        icon = await get_setting(f"icon_{key}", "")
        built.append(
            await _btn(
                text,
                callback_data=cb,
                style=style or default_style,
                icon_custom_emoji_id=icon or None,
            )
        )

    rows = []
    for i in range(0, len(built), 2):
        chunk = built[i : i + 2]
        rows.append(chunk)

    # Full-width Settings row at bottom
    settings_text = get_text(lang, "btn_settings")
    rows.append([
        await _btn(settings_text, callback_data="menu:settings", style="primary"),
    ])

    return InlineKeyboardMarkup(inline_keyboard=rows)


async def settings_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            await _btn(get_text(lang, "btn_change_language"), callback_data="settings:lang", style="success"),
        ],
        [
            await _btn(get_text(lang, "btn_status"), callback_data="menu:status", style="primary"),
            await _btn(get_text(lang, "btn_support"), callback_data="menu:support", style="primary"),
        ],
        [
            await _btn(get_text(lang, "btn_back"), callback_data="menu:back", style="primary"),
        ],
    ])


async def settings_language_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇬🇧 English", callback_data="lang:en", style="primary"),
            InlineKeyboardButton(text="🇧🇩 বাংলা", callback_data="lang:bn", style="success"),
        ],
        [
            await _btn(get_text(lang, "btn_back"), callback_data="menu:settings", style="primary"),
        ],
    ])


async def premium_keyboard(lang: str, register_url: str) -> InlineKeyboardMarkup:
    btn_register = await get_setting("btn_register", get_text(lang, "btn_register"))
    btn_back = await get_setting("btn_back", get_text(lang, "btn_back"))
    style_reg = await get_setting("style_btn_register", "success")
    style_back = await get_setting("style_btn_back", "primary")
    icon_reg = await get_setting("icon_btn_register", "")
    icon_back = await get_setting("icon_btn_back", "")
    return InlineKeyboardMarkup(inline_keyboard=[
        [await _btn(btn_register, url=register_url, style=style_reg, icon_custom_emoji_id=icon_reg or None)],
        [await _btn(btn_back, callback_data="menu:back", style=style_back, icon_custom_emoji_id=icon_back or None)],
    ])


async def back_keyboard(lang: str) -> InlineKeyboardMarkup:
    btn_back = await get_setting("btn_back", get_text(lang, "btn_back"))
    style_back = await get_setting("style_btn_back", "primary")
    icon_back = await get_setting("icon_btn_back", "")
    return InlineKeyboardMarkup(inline_keyboard=[
        [await _btn(btn_back, callback_data="menu:back", style=style_back, icon_custom_emoji_id=icon_back or None)],
    ])
