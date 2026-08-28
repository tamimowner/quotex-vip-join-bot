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


def add_bold(entities: list[MessageEntity], text: str, start_utf16: int, length_utf16: int) -> None:
    entities.append(
        MessageEntity(
            type=MessageEntityType.BOLD,
            offset=start_utf16,
            length=length_utf16,
        )
    )


def create_account_message(lang: str, register_url: str, min_deposit: int) -> tuple[str, list[MessageEntity]]:
    """Exact create-account caption with premium custom emoji."""
    if (lang or "bn").lower() == "en":
        parts = [
            ("⭐", "6129909635613726974"),
            (" How to create a new Quotex account\n\n", None),
            ("•", "6217713374327738118"),
            (" Click the Register button below\n", None),
            ("•", "6217713374327738118"),
            (" Fill the form with a new email/phone\n", None),
            ("•", "6217713374327738118"),
            (" Complete registration\n", None),
            ("•", "6217713374327738118"),
            (f" Make minimum deposit ${min_deposit}\n", None),
            ("•", "6217713374327738118"),
            (" Send Trader ID to the bot\n\n", None),
            ("🔗", "5938264290740933445"),
            (f" Only our Affiliate Link = {register_url}\nis accepted. ", None),
            ("✅", "6217732620076191135"),
        ]
    else:
        parts = [
            ("⭐", "6129909635613726974"),
            (" কীভাবে নতুন কোটেক্স অ্যাকাউন্ট তৈরি করবেন\n\n", None),
            ("•", "6217713374327738118"),
            (" নিচের রেজিস্টার বাটনে ক্লিক করুন\n", None),
            ("•", "6217713374327738118"),
            (" নতুন ইমেইল/ফোন দিয়ে ফর্ম পূরণ করুন\n", None),
            ("•", "6217713374327738118"),
            (" রেজিস্ট্রেশন শেষ করুন\n", None),
            ("•", "6217713374327738118"),
            (f" মিনিমাম ডিপোজিট করুন ${min_deposit}\n", None),
            ("•", "6217713374327738118"),
            (" বটে Trader ID পাঠান\n\n", None),
            ("🔗", "5938264290740933445"),
            (f" শুধু আমাদের Affiliate Link = {register_url}\nগ্রহণযোগ্য। ", None),
            ("✅", "6217732620076191135"),
        ]
    text, entities = build_parts(parts)
    # Bold title (after first emoji)
    title = (
        " How to create a new Quotex account"
        if (lang or "bn").lower() == "en"
        else " কীভাবে নতুন কোটেক্স অ্যাকাউন্ট তৈরি করবেন"
    )
    # offset of title starts after first emoji (1 utf16 unit typically)
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
