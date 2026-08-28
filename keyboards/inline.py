from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from locales import get_text
from services.settings_store import get_setting, get_button_text


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
        text = await get_button_text(key, lang)
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
        rows.append(built[i : i + 2])

    settings_text = await get_button_text("btn_settings", lang)
    rows.append([
        await _btn(settings_text, callback_data="menu:settings", style="primary"),
    ])

    return InlineKeyboardMarkup(inline_keyboard=rows)


async def settings_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            await _btn(
                get_text(lang, "btn_change_language"),
                callback_data="settings:lang",
                style="success",
            ),
        ],
        [
            await _btn(await get_button_text("btn_status", lang), callback_data="menu:status", style="primary"),
            await _btn(await get_button_text("btn_support", lang), callback_data="menu:support", style="primary"),
        ],
        [
            await _btn(await get_button_text("btn_back", lang), callback_data="menu:back", style="primary"),
        ],
    ])


async def settings_language_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇬🇧 English", callback_data="lang:en", style="primary"),
            InlineKeyboardButton(text="🇧🇩 বাংলা", callback_data="lang:bn", style="success"),
        ],
        [
            await _btn(await get_button_text("btn_back", lang), callback_data="menu:settings", style="primary"),
        ],
    ])


async def premium_keyboard(lang: str, register_url: str) -> InlineKeyboardMarkup:
    """Default register + back (premium flow)."""
    btn_register = await get_button_text("btn_register", lang)
    btn_back = await get_button_text("btn_back", lang)
    style_reg = await get_setting("style_btn_register", "success")
    style_back = await get_setting("style_btn_back", "primary")
    icon_reg = await get_setting("icon_btn_register", "")
    icon_back = await get_setting("icon_btn_back", "")
    return InlineKeyboardMarkup(inline_keyboard=[
        [await _btn(btn_register, url=register_url, style=style_reg, icon_custom_emoji_id=icon_reg or None)],
        [await _btn(btn_back, callback_data="menu:back", style=style_back, icon_custom_emoji_id=icon_back or None)],
    ])


async def verify_fail_keyboard(lang: str, register_url: str) -> InlineKeyboardMarkup:
    """
    When trader_id is not from our affiliate link:
    1) Open Quotex Account (partner link)
    2) Tutorial (YouTube / admin-set URL)
    """
    open_text = await get_button_text("btn_open_account", lang)
    if not open_text or open_text == "btn_open_account":
        open_text = get_text(lang, "btn_open_account")

    tut_text = await get_button_text("btn_tutorial", lang)
    if not tut_text or tut_text == "btn_tutorial":
        tut_text = get_text(lang, "btn_tutorial")

    tutorial_url = (await get_setting("tutorial_url", "") or "").strip()
    if not tutorial_url:
        tutorial_url = "https://www.youtube.com"

    rows = [
        [await _btn(open_text, url=register_url, style="success")],
    ]
    if tutorial_url.startswith("http"):
        rows.append([await _btn(tut_text, url=tutorial_url, style="primary")])

    return InlineKeyboardMarkup(inline_keyboard=rows)


async def back_keyboard(lang: str) -> InlineKeyboardMarkup:
    btn_back = await get_button_text("btn_back", lang)
    style_back = await get_setting("style_btn_back", "primary")
    icon_back = await get_setting("icon_btn_back", "")
    return InlineKeyboardMarkup(inline_keyboard=[
        [await _btn(btn_back, callback_data="menu:back", style=style_back, icon_custom_emoji_id=icon_back or None)],
    ])
