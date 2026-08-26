from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from locales import get_text


def language_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇬🇧 English", callback_data="lang:en"),
            InlineKeyboardButton(text="🇧🇩 বাংলা", callback_data="lang:bn"),
        ]
    ])


def main_menu(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(lang, "btn_premium"), callback_data="menu:premium")],
        [InlineKeyboardButton(text=get_text(lang, "btn_create_account"), callback_data="menu:create")],
        [InlineKeyboardButton(text=get_text(lang, "btn_delete_account"), callback_data="menu:delete")],
        [InlineKeyboardButton(text=get_text(lang, "btn_public"), callback_data="menu:public")],
        [InlineKeyboardButton(text=get_text(lang, "btn_status"), callback_data="menu:status")],
        [InlineKeyboardButton(text=get_text(lang, "btn_support"), callback_data="menu:support")],
    ])


def premium_keyboard(lang: str, register_url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(lang, "btn_register"), url=register_url)],
        [InlineKeyboardButton(text=get_text(lang, "btn_back"), callback_data="menu:back")],
    ])


def back_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(lang, "btn_back"), callback_data="menu:back")],
    ])
