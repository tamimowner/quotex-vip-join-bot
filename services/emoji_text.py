"""Build Telegram messages with custom premium emoji via MessageEntity."""
from aiogram.types import MessageEntity
from aiogram.enums import MessageEntityType


def utf16_len(s: str) -> int:
    return len(s.encode("utf-16-le")) // 2


def build_parts(parts: list[tuple[str, str | None]]) -> tuple[str, list[MessageEntity]]:
    """
    parts: list of (text, custom_emoji_id or None).
    When emoji_id is set, `text` should be a short fallback (usually 1 symbol).
    """
    chunks: list[str] = []
    entities: list[MessageEntity] = []
    offset = 0
    for text, eid in parts:
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
        chunks.append(text)
        offset += length
    return "".join(chunks), entities


def create_account_message(lang: str, register_url: str, min_deposit: int) -> tuple[str, list[MessageEntity]]:
    """Create-account guide with premium custom emoji (user-provided text)."""
    url = (register_url or "").strip()
    is_en = (lang or "bn").lower() == "en"

    if is_en:
        title = " How to create a new Quotex account"
        parts = [
            ("⭐", "6105169455757661838"),
            (title + "\n\n", None),
            ("1️⃣", "5938069973535559743"),
            (" Click my link:\n", None),
            ("🔗", "5042101437237036298"),
            (f" {url}\n\n", None),
            ("2️⃣", "5938069973535559743"),
            (" Select country, enter new email and strong password ", None),
            ("🔐", "6095821244689554590"),
            ("\n\n", None),
            ("3️⃣", "5938069973535559743"),
            (" Accept the terms\n\n", None),
            ("4️⃣", "5938069973535559743"),
            (" Click Register – account registration successful.\n\n", None),
            ("5️⃣", "5938069973535559743"),
            (
                " Check your email – you will get a verification link – verify your email.\n\n",
                None,
            ),
            ("6️⃣", "5938069973535559743"),
            (
                " Then go to Profile and verify the account with Documents (Identity Verification).\n\n",
                None,
            ),
            ("✅", "6273749318717412886"),
            (" Done! Your account is ready for deposit.", None),
        ]
    else:
        title = " কীভাবে একটি নতুন Quotex অ্যাকাউন্ট তৈরি করবেন"
        parts = [
            ("⭐", "6105169455757661838"),
            (title + "\n\n", None),
            ("১", "5938069973535559743"),
            (". আমার লিংকে ক্লিক করুন:\n", None),
            ("🔗", "5042101437237036298"),
            (f" {url}\n\n", None),
            ("২", "5938069973535559743"),
            (". দেশ নির্বাচন করুন, নতুন ইমেইল এবং শক্তিশালী পাসওয়ার্ড দিন ", None),
            ("🔐", "6095821244689554590"),
            ("\n\n", None),
            ("৩", "5938069973535559743"),
            (". শর্তাবলী গ্রহণ করুন\n\n", None),
            ("৪", "5938069973535559743"),
            (". রেজিস্ট্রেশন ক্লিক করুন – অ্যাকাউন্ট রেজিস্ট্রেশন সফল হয়েছে।\n\n", None),
            ("৫", "5938069973535559743"),
            (
                ". আপনার ইমেইল চেক করুন – আপনি ভেরিফিকেশনের জন্য একটি লিংক পাবেন – আপনার ইমেইল ভেরিফাই করুন।\n\n",
                None,
            ),
            ("৬", "5938069973535559743"),
            (
                ". তারপর আপনার প্রোফাইলে যান এবং ডকুমেন্টস (আইডেন্টিটি ভেরিফিকেশন) দিয়ে অ্যাকাউন্ট ভেরিফাই করুন।\n\n",
                None,
            ),
            ("✅", "6273749318717412886"),
            (" সম্পন্ন! আপনার অ্যাকাউন্ট ডিপোজিটের জন্য প্রস্তুত।", None),
        ]

    text, entities = build_parts(parts)

    # Bold title
    title_start = utf16_len(parts[0][0])
    entities.insert(
        0,
        MessageEntity(
            type=MessageEntityType.BOLD,
            offset=title_start,
            length=utf16_len(title),
        ),
    )

    # Clickable URL on the affiliate link line
    if url.startswith("http"):
        # find url offset in full text
        idx = text.find(url)
        if idx >= 0:
            # utf16 offset of url
            prefix = text[:idx]
            entities.append(
                MessageEntity(
                    type=MessageEntityType.URL,
                    offset=utf16_len(prefix),
                    length=utf16_len(url),
                )
            )

    return text, entities


def delete_account_message(lang: str) -> tuple[str, list[MessageEntity]]:
    if (lang or "bn").lower() == "en":
        parts = [
            ("❌", "5298742255912235479"),
            (" How to delete old Quotex account\n\n", None),
            ("1", "5235547326889608764"),
            (". Login to old account\n", None),
            ("2", "5235547326889608764"),
            (". Profile / Settings\n", None),
            ("3", "5235919365546724452"),
            (". Request account deletion\n", None),
            ("4", "5238105937692085546"),
            (". Create a new account with our link", None),
        ]
        title = " How to delete old Quotex account"
    else:
        parts = [
            ("❌", "5298742255912235479"),
            (" কীভাবে পুরাতন কোটেক্স অ্যাকাউন্ট ডিলিট করবেন\n\n", None),
            ("1", "5235547326889608764"),
            (". পুরোনো অ্যাকাউন্টে লগইন\n", None),
            ("2", "5235547326889608764"),
            (". প্রোফাইল / সেটিংস\n", None),
            ("3", "5235919365546724452"),
            (". অ্যাকাউন্ট ডিলিট রিকোয়েস্ট\n", None),
            ("4", "5238105937692085546"),
            (". আমাদের লিংক দিয়ে নতুন অ্যাকাউন্ট তৈরি", None),
        ]
        title = " কীভাবে পুরাতন কোটেক্স অ্যাকাউন্ট ডিলিট করবেন"
    text, entities = build_parts(parts)
    title_start = utf16_len(parts[0][0])
    entities.insert(
        0,
        MessageEntity(
            type=MessageEntityType.BOLD,
            offset=title_start,
            length=utf16_len(title),
        ),
    )
    return text, entities
