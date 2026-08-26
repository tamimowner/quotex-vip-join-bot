from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from locales import get_text
from services.settings_store import get_setting


def language_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇬🇧 English", callback_data="lang:en"),
            InlineKeyboardButton(text="🇧🇩 বাংলা", callback_data="lang:bn"),
        ]
    ])


async def main_menu(lang: str) -> InlineKeyboardMarkup:
    btn_premium = await get_setting("btn_premium", get_text(lang, "btn_premium"))
    btn_create = await get_setting("btn_create_account", get_text(lang, "btn_create_account"))
    btn_delete = await get_setting("btn_delete_account", get_text(lang, "btn_delete_account"))
    btn_public = await get_setting("btn_public", get_text(lang, "btn_public"))
    btn_status = await get_setting("btn_status", get_text(lang, "btn_status"))
    btn_support = await get_setting("btn_support", get_text(lang, "btn_support"))
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=btn_premium, callback_data="menu:premium")],
        [InlineKeyboardButton(text=btn_create, callback_data="menu:create")],
        [InlineKeyboardButton(text=btn_delete, callback_data="menu:delete")],
        [InlineKeyboardButton(text=btn_public, callback_data="menu:public")],
        [InlineKeyboardButton(text=btn_status, callback_data="menu:status")],
        [InlineKeyboardButton(text=btn_support, callback_data="menu:support")],
    ])


async def premium_keyboard(lang: str, register_url: str) -> InlineKeyboardMarkup:
    btn_register = await get_setting("btn_register", get_text(lang, "btn_register"))
    btn_back = await get_setting("btn_back", get_text(lang, "btn_back"))
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=btn_register, url=register_url)],
        [InlineKeyboardButton(text=btn_back, callback_data="menu:back")],
    ])


async def back_keyboard(lang: str) -> InlineKeyboardMarkup:
    btn_back = await get_setting("btn_back", get_text(lang, "btn_back"))
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=btn_back, callback_data="menu:back")],
    ])
