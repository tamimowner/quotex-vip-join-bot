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
    """Create-account guide — only custom premium emoji."""
    url = (register_url or "").strip()
    is_en = (lang or "bn").lower() == "en"

    # Custom emoji IDs (from user)
    E_TITLE = "6105169455757661838"   # ✨
    E_STEP  = "5938069973535559743"   # ➡️
    E_LINK  = "5042101437237036298"   # 🔗
    E_PASS  = "6095821244689554590"   # 🔑
    E_DONE  = "6273749318717412886"   # ✅

    if is_en:
        parts = [
            ("✨", E_TITLE),
            (" How to create a new Quotex account", None, True),
            ("\n\n", None),
            ("➡️", E_STEP),
            (" 1. Click my link:\n", None),
            ("🔗", E_LINK),
            (f" {url}\n\n", None),
            ("➡️", E_STEP),
            (" 2. Select country, new email and strong password ", None),
            ("🔑", E_PASS),
            ("\n\n", None),
            ("➡️", E_STEP),
            (" 3. Accept the terms\n\n", None),
            ("➡️", E_STEP),
            (" 4. Click Register – account registration successful.\n\n", None),
            ("➡️", E_STEP),
            (" 5. Check your email – you will get a verification link – verify your email.\n\n", None),
            ("➡️", E_STEP),
            (" 6. Then go to Profile and verify account with Documents (Identity Verification).\n\n", None),
            ("✅", E_DONE),
            (" Done! Your account is ready for deposit.", None),
        ]
    else:
        parts = [
            ("✨", E_TITLE),
            (" কীভাবে একটি নতুন Quotex অ্যাকাউন্ট তৈরি করবেন", None, True),
            ("\n\n", None),
            ("➡️", E_STEP),
            (" ১. আমার লিংকে ক্লিক করুন:\n", None),
            ("🔗", E_LINK),
            (f" {url}\n\n", None),
            ("➡️", E_STEP),
            (" ২. দেশ নির্বাচন করুন, নতুন ইমেইল এবং শক্তিশালী পাসওয়ার্ড দিন ", None),
            ("🔑", E_PASS),
            ("\n\n", None),
            ("➡️", E_STEP),
            (" ৩. শর্তাবলী গ্রহণ করুন\n\n", None),
            ("➡️", E_STEP),
            (" ৪. রেজিস্ট্রেশন ক্লিক করুন – অ্যাকাউন্ট রেজিস্ট্রেশন সফল হয়েছে।\n\n", None),
            ("➡️", E_STEP),
            (" ৫. আপনার ইমেইল চেক করুন – আপনি ভেরিফিকেশনের জন্য একটি লিংক পাবেন – আপনার ইমেইল ভেরিফাই করুন।\n\n", None),
            ("➡️", E_STEP),
            (" ৬. তারপর আপনার প্রোফাইলে যান এবং ডকুমেন্টস (আইডেন্টিটি ভেরিফিকেশন) দিয়ে অ্যাকাউন্ট ভেরিফাই করুন।\n\n", None),
            ("✅", E_DONE),
            (" সম্পন্ন! আপনার অ্যাকাউন্ট ডিপোজিটের জন্য প্রস্তুত।", None),
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
    """Delete-account guide — only custom premium emoji (screenshot style)."""
    # Re-use same custom IDs for consistency + title
    E_TITLE = "5298742255912235479"   # ❌
    E_STEP  = "5938069973535559743"   # ➡️
    E_DONE  = "6273749318717412886"   # ✅

    if (lang or "bn").lower() == "en":
        parts = [
            ("❌", E_TITLE),
            (" How to delete your old Quotex account", None, True),
            ("\n\n", None),
            ("➡️", E_STEP),
            (" 1. Go to Profile option\n\n", None),
            ("➡️", E_STEP),
            (" 2. Scroll down and select Account Delete\n\n", None),
            ("➡️", E_STEP),
            (" 3. Check your email – you will get a link to delete the account\n\n", None),
            ("➡️", E_STEP),
            (" 4. Click the link in email – account deleted successfully.\n\n", None),
            ("✅", E_DONE),
            (" Now you can register a new account using our affiliate link.", None),
        ]
    else:
        parts = [
            ("❌", E_TITLE),
            (" কীভাবে আপনার পুরাতন Quotex অ্যাকাউন্ট ডিলিট করবেন", None, True),
            ("\n\n", None),
            ("➡️", E_STEP),
            (" ১. প্রোফাইল অপশনে যান\n\n", None),
            ("➡️", E_STEP),
            (" ২. নিচে স্ক্রোল করুন এবং অ্যাকাউন্ট ডিলিট সিলেক্ট করুন\n\n", None),
            ("➡️", E_STEP),
            (" ৩. আপনার ইমেইল চেক করুন – আপনি অ্যাকাউন্ট ডিলিট করার জন্য একটি লিংক পাবেন\n\n", None),
            ("➡️", E_STEP),
            (" ৪. ইমেইলে প্রাপ্ত লিংকে ক্লিক করুন – অ্যাকাউন্ট সফলভাবে ডিলিট হয়েছে।\n\n", None),
            ("✅", E_DONE),
            (" এখন আপনি আমাদের অ্যাফিলিয়েট লিংক ব্যবহার করে একটি নতুন অ্যাকাউন্ট রেজিস্ট্রেশন করতে পারেন।", None),
        ]

    return build_parts(parts)
