from locales import get_text
from services.settings_store import get_setting


async def get_message_text(lang: str, key: str, **kwargs) -> str:
    """DB override msg_{key}_{lang} then locale fallback."""
    lang = (lang or "bn").lower()
    if lang not in ("bn", "en"):
        lang = "bn"
    custom = await get_setting(f"msg_{key}_{lang}", "")
    text = custom if custom else get_text(lang, key)
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text
