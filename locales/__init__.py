from locales.en import TEXTS as EN
from locales.bn import TEXTS as BN

LOCALES = {
    "en": EN,
    "bn": BN,
}

def get_text(lang: str, key: str, **kwargs) -> str:
    texts = LOCALES.get(lang, BN)
    text = texts.get(key, key)
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text
