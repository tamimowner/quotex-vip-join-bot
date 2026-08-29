"""Build Telegram messages with custom premium emoji via MessageEntity."""
from aiogram.types import MessageEntity
from aiogram.enums import MessageEntityType


def utf16_len(s: str) -> int:
    return len(s.encode("utf-16-le")) // 2


def build_parts(
    parts: list[tuple],
) -> tuple[str, list[MessageEntity]]:
    """
    parts items:
      (text, emoji_id|None)
      or (text, emoji_id|None, bold: bool)
    When emoji_id is set, text should be a short fallback (1 symbol preferred).
    """
    chunks: list[str] = []
    entities: list[MessageEntity] = []
    offset = 0
    for item in parts:
        if not item:
            continue
        text = item[0]
        eid = item[1] if len(item) > 1 else None
        bold = bool(item[2]) if len(item) > 2 else False
        if text is None or text == "":
            continue
        length = utf16_len(text)
        if eid:
            entities.append(
                MessageEntity(
                    type=MessageEntityType.CUSTOM_EMOJI,
                    offset=offset,
                    length=length,
                    custom_emoji_id=str(eid),
                )
            )
        if bold:
            entities.append(
                MessageEntity(
                    type=MessageEntityType.BOLD,
                    offset=offset,
                    length=length,
                )
            )
        chunks.append(text)
        offset += length
    return "".join(chunks), entities


def create_account_message(lang: str, register_url: str, min_deposit: int) -> tuple[str, list[MessageEntity]]:
    """Create-account guide — premium custom emoji + bold steps."""
    url = (register_url or "").strip()
    is_en = (lang or "bn").lower() == "en"

    # Emoji IDs from admin
    E_TITLE = "6105169455757661838"
    E_STEP = "5938069973535559743"
    E_LINK = "5042101437237036298"
    E_PASS = "6095821244689554590"
    E_DONE = "6273749318717412886"

    if is_en:
        parts = [
            ("⭐", E_TITLE),
            (" How to create a new Quotex account", None, True),
            ("\n━━━━━━━━━━━━━━━━\n\n", None),
            ("•", E_STEP),
            (" 1. Click my link:", None, True),
            ("\n", None),
            ("🔗", E_LINK),
            (f" {url}\n\n", None),
            ("•", E_STEP),
            (" 2. Select country, new email & strong password ", None, True),
            ("🔐", E_PASS),
            ("\n\n", None),
            ("•", E_STEP),
            (" 3. Accept the terms", None, True),
            ("\n\n", None),
            ("•", E_STEP),
            (" 4. Click Register – registration successful.", None, True),
            ("\n\n", None),
            ("•", E_STEP),
            (" 5. Check email – open verification link – verify email.", None, True),
            ("\n\n", None),
            ("•", E_STEP),
            (" 6. Go to Profile → Documents (Identity Verification).", None, True),
            ("\n\n━━━━━━━━━━━━━━━━\n", None),
            ("✅", E_DONE),
            (" Done! Your account is ready for deposit.", None, True),
        ]
    else:
        parts = [
            ("⭐", E_TITLE),
            (" কীভাবে একটি নতুন Quotex অ্যাকাউন্ট তৈরি করবেন", None, True),
            ("\n━━━━━━━━━━━━━━━━\n\n", None),
            ("•", E_STEP),
            (" ১. আমার লিংকে ক্লিক করুন:", None, True),
            ("\n", None),
            ("🔗", E_LINK),
            (f" {url}\n\n", None),
            ("•", E_STEP),
            (" ২. দেশ নির্বাচন করুন, নতুন ইমেইল এবং শক্তিশালী পাসওয়ার্ড দিন ", None, True),
            ("🔐", E_PASS),
            ("\n\n", None),
            ("•", E_STEP),
            (" ৩. শর্তাবলী গ্রহণ করুন", None, True),
            ("\n\n", None),
            ("•", E_STEP),
            (" ৪. রেজিস্ট্রেশন ক্লিক করুন – অ্যাকাউন্ট রেজিস্ট্রেশন সফল হয়েছে।", None, True),
            ("\n\n", None),
            ("•", E_STEP),
            (
                " ৫. আপনার ইমেইল চেক করুন – ভেরিফিকেশন লিংক পাবেন – ইমেইল ভেরিফাই করুন।",
                None,
                True,
            ),
            ("\n\n", None),
            ("•", E_STEP),
            (
                " ৬. প্রোফাইলে যান এবং ডকুমেন্টস (আইডেন্টিটি ভেরিফিকেশন) দিয়ে অ্যাকাউন্ট ভেরিফাই করুন।",
                None,
                True,
            ),
            ("\n\n━━━━━━━━━━━━━━━━\n", None),
            ("✅", E_DONE),
            (" সম্পন্ন! আপনার অ্যাকাউন্ট ডিপোজিটের জন্য প্রস্তুত।", None, True),
        ]

    text, entities = build_parts(parts)

    if url.startswith("http"):
        idx = text.find(url)
        if idx >= 0:
            prefix = text[:idx]
            entities.append(
                MessageEntity(
                    type=MessageEntityType.TEXT_LINK,
                    offset=utf16_len(prefix),
                    length=utf16_len(url),
                    url=url,
                )
            )

    return text, entities


def delete_account_message(lang: str) -> tuple[str, list[MessageEntity]]:
    E_TITLE = "5298742255912235479"
    E1 = "5235547326889608764"
    E2 = "5235547326889608764"
    E3 = "5235919365546724452"
    E4 = "5238105937692085546"

    if (lang or "bn").lower() == "en":
        parts = [
            ("❌", E_TITLE),
            (" How to delete old Quotex account", None, True),
            ("\n━━━━━━━━━━━━━━━━\n\n", None),
            ("1", E1),
            (". Login to old account\n\n", None, True),
            ("2", E2),
            (". Profile / Settings\n\n", None, True),
            ("3", E3),
            (". Request account deletion\n\n", None, True),
            ("4", E4),
            (". Create a new account with our link", None, True),
        ]
    else:
        parts = [
            ("❌", E_TITLE),
            (" কীভাবে পুরাতন কোটেক্স অ্যাকাউন্ট ডিলিট করবেন", None, True),
            ("\n━━━━━━━━━━━━━━━━\n\n", None),
            ("1", E1),
            (". পুরোনো অ্যাকাউন্টে লগইন\n\n", None, True),
            ("2", E2),
            (". প্রোফাইল / সেটিংস\n\n", None, True),
            ("3", E3),
            (". অ্যাকাউন্ট ডিলিট রিকোয়েস্ট\n\n", None, True),
            ("4", E4),
            (". আমাদের লিংক দিয়ে নতুন অ্যাকাউন্ট তৈরি", None, True),
        ]

    return build_parts(parts)
