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
    kwargs: dict = {"text": text or "·"}
    if callback_data:
        kwargs["callback_data"] = callback_data
    if url and str(url).startswith("http"):
        kwargs["url"] = str(url).strip()
    elif url and not callback_data:
        # Invalid URL without callback — use dummy callback so button still works
        kwargs["callback_data"] = "menu:back"
    if style in ("primary", "success", "danger"):
        kwargs["style"] = style
    if icon_custom_emoji_id:
        kwargs["icon_custom_emoji_id"] = str(icon_custom_emoji_id)
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
        if not text or text == key:
            text = get_text(lang, key) or key
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
    if not settings_text or settings_text == "btn_settings":
        settings_text = get_text(lang, "btn_settings") or "Settings"
    rows.append([
        await _btn(settings_text, callback_data="menu:settings", style="primary"),
    ])

    return InlineKeyboardMarkup(inline_keyboard=rows)


async def settings_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            await _btn(
                get_text(lang, "btn_change_language") or "Language",
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
    """Register URL button + back."""
    btn_register = await get_button_text("btn_register", lang)
    if not btn_register or btn_register == "btn_register":
        btn_register = get_text(lang, "btn_register") or "Register"
    btn_back = await get_button_text("btn_back", lang)
    if not btn_back or btn_back == "btn_back":
        btn_back = get_text(lang, "btn_back") or "Back"

    style_reg = await get_setting("style_btn_register", "success")
    style_back = await get_setting("style_btn_back", "primary")
    icon_reg = await get_setting("icon_btn_register", "")
    icon_back = await get_setting("icon_btn_back", "")

    rows = []
    url = (register_url or "").strip()
    if url.startswith("http"):
        rows.append([
            await _btn(
                btn_register,
                url=url,
                style=style_reg or "success",
                icon_custom_emoji_id=icon_reg or None,
            )
        ])
    rows.append([
        await _btn(
            btn_back,
            callback_data="menu:back",
            style=style_back or "primary",
            icon_custom_emoji_id=icon_back or None,
        )
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)


async def verify_fail_keyboard(lang: str, register_url: str) -> InlineKeyboardMarkup:
    open_text = await get_button_text("btn_open_account", lang)
    if not open_text or open_text == "btn_open_account":
        open_text = get_text(lang, "btn_open_account") or "Open Account"

    tut_text = await get_button_text("btn_tutorial", lang)
    if not tut_text or tut_text == "btn_tutorial":
        tut_text = get_text(lang, "btn_tutorial") or "Tutorial"

    tutorial_url = (await get_setting("tutorial_url", "") or "").strip()
    if not tutorial_url:
        tutorial_url = "https://www.youtube.com"

    rows = []
    url = (register_url or "").strip()
    if url.startswith("http"):
        rows.append([await _btn(open_text, url=url, style="success")])
    if tutorial_url.startswith("http"):
        rows.append([await _btn(tut_text, url=tutorial_url, style="primary")])
    if not rows:
        rows.append([await _btn(get_text(lang, "btn_back") or "Back", callback_data="menu:back")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


async def back_keyboard(lang: str) -> InlineKeyboardMarkup:
    btn_back = await get_button_text("btn_back", lang)
    if not btn_back or btn_back == "btn_back":
        btn_back = get_text(lang, "btn_back") or "Back"
    style_back = await get_setting("style_btn_back", "primary")
    icon_back = await get_setting("icon_btn_back", "")
    return InlineKeyboardMarkup(inline_keyboard=[
        [await _btn(btn_back, callback_data="menu:back", style=style_back, icon_custom_emoji_id=icon_back or None)],
    ])
