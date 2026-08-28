from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from locales import get_text
from services.settings_store import get_setting, get_button_text

# Default custom emoji IDs (admin can override via /admin → প্রিমিয়াম ইমোজি)
DEFAULT_ICONS = {
    "btn_create_account": "6129909635613726974",
    "btn_delete_account": "5298742255912235479",
    "btn_premium": "5206607081334906820",
    "btn_status": "6131664675214987967",
    "btn_public": "5856956664292315353",
    "btn_support": "5039783602301175152",
    "btn_register": "6217732620076191135",
    "btn_open_account": "6214983170991853422",
    "btn_tutorial": "5814161253672687027",
    "btn_back": "6300891304414938793",
    "btn_settings": "",
}


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
        kwargs["callback_data"] = "menu:back"
    if style in ("primary", "success", "danger"):
        kwargs["style"] = style
    # icon_custom_emoji_id must be numeric string
    if icon_custom_emoji_id:
        eid = str(icon_custom_emoji_id).strip()
        if eid.isdigit():
            kwargs["icon_custom_emoji_id"] = eid
    return InlineKeyboardButton(**kwargs)


async def _icon_for(key: str) -> str | None:
    """DB icon first, else default pack id."""
    saved = (await get_setting(f"icon_{key}", "") or "").strip()
    if saved and saved.isdigit():
        return saved
    default = DEFAULT_ICONS.get(key, "")
    return default if default else None


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
        icon = await _icon_for(key)
        built.append(
            await _btn(
                text,
                callback_data=cb,
                style=style or default_style,
                icon_custom_emoji_id=icon,
            )
        )

    rows = []
    for i in range(0, len(built), 2):
        rows.append(built[i : i + 2])

    settings_text = await get_button_text("btn_settings", lang)
    if not settings_text or settings_text == "btn_settings":
        settings_text = get_text(lang, "btn_settings") or "Settings"
    rows.append([
        await _btn(
            settings_text,
            callback_data="menu:settings",
            style="primary",
            icon_custom_emoji_id=await _icon_for("btn_settings"),
        ),
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
            await _btn(
                await get_button_text("btn_status", lang),
                callback_data="menu:status",
                style="primary",
                icon_custom_emoji_id=await _icon_for("btn_status"),
            ),
            await _btn(
                await get_button_text("btn_support", lang),
                callback_data="menu:support",
                style="primary",
                icon_custom_emoji_id=await _icon_for("btn_support"),
            ),
        ],
        [
            await _btn(
                await get_button_text("btn_back", lang),
                callback_data="menu:back",
                style="primary",
                icon_custom_emoji_id=await _icon_for("btn_back"),
            ),
        ],
    ])


async def settings_language_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇬🇧 English", callback_data="lang:en", style="primary"),
            InlineKeyboardButton(text="🇧🇩 বাংলা", callback_data="lang:bn", style="success"),
        ],
        [
            await _btn(
                await get_button_text("btn_back", lang),
                callback_data="menu:settings",
                style="primary",
                icon_custom_emoji_id=await _icon_for("btn_back"),
            ),
        ],
    ])


async def premium_keyboard(lang: str, register_url: str) -> InlineKeyboardMarkup:
    btn_register = await get_button_text("btn_register", lang)
    if not btn_register or btn_register == "btn_register":
        btn_register = get_text(lang, "btn_register") or "Register"
    btn_back = await get_button_text("btn_back", lang)
    if not btn_back or btn_back == "btn_back":
        btn_back = get_text(lang, "btn_back") or "Back"

    style_reg = await get_setting("style_btn_register", "success")
    style_back = await get_setting("style_btn_back", "primary")

    rows = []
    url = (register_url or "").strip()
    if url.startswith("http"):
        rows.append([
            await _btn(
                btn_register,
                url=url,
                style=style_reg or "success",
                icon_custom_emoji_id=await _icon_for("btn_register"),
            )
        ])
    rows.append([
        await _btn(
            btn_back,
            callback_data="menu:back",
            style=style_back or "primary",
            icon_custom_emoji_id=await _icon_for("btn_back"),
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
        rows.append([
            await _btn(
                open_text,
                url=url,
                style="success",
                icon_custom_emoji_id=await _icon_for("btn_open_account"),
            )
        ])
    if tutorial_url.startswith("http"):
        rows.append([
            await _btn(
                tut_text,
                url=tutorial_url,
                style="primary",
                icon_custom_emoji_id=await _icon_for("btn_tutorial"),
            )
        ])
    if not rows:
        rows.append([
            await _btn(
                get_text(lang, "btn_back") or "Back",
                callback_data="menu:back",
                icon_custom_emoji_id=await _icon_for("btn_back"),
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=rows)


async def back_keyboard(lang: str) -> InlineKeyboardMarkup:
    btn_back = await get_button_text("btn_back", lang)
    if not btn_back or btn_back == "btn_back":
        btn_back = get_text(lang, "btn_back") or "Back"
    style_back = await get_setting("style_btn_back", "primary")
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            await _btn(
                btn_back,
                callback_data="menu:back",
                style=style_back,
                icon_custom_emoji_id=await _icon_for("btn_back"),
            )
        ],
    ])
