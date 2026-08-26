from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import os


def normalize_database_url(url: str) -> str:
    """Railway gives postgresql:// — SQLAlchemy async needs postgresql+asyncpg://"""
    if not url:
        return url
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    if url.startswith("postgresql://") and "+asyncpg" not in url:
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    BOT_TOKEN: str
    ADMIN_IDS: str = ""
    VIP_GROUP_ID: int = 0

    AFFILIATE_LINK_BASE: str = (
        "https://broker-qx.pro/sign-up/?lid=1480996&click_id={click_id}&site_id={site_id}"
    )
    SITE_ID: str = "1"

    DATABASE_URL: str

    POSTBACK_SECRET: str = ""
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    DEFAULT_LANGUAGE: str = "bn"

    @property
    def admin_ids(self) -> List[int]:
        if not self.ADMIN_IDS:
            return []
        return [int(x.strip()) for x in self.ADMIN_IDS.split(",") if x.strip()]

    @property
    def database_url(self) -> str:
        return normalize_database_url(self.DATABASE_URL)


# Build settings; fail with clear message
try:
    settings = Settings()
    # Prefer Railway-injected PORT
    if os.getenv("PORT"):
        object.__setattr__(settings, "PORT", int(os.getenv("PORT")))
except Exception as e:
    print("ERROR: Missing or invalid environment variables:", e)
    print("Required: BOT_TOKEN, DATABASE_URL")
    print("Recommended: VIP_GROUP_ID, ADMIN_IDS, AFFILIATE_LINK_BASE")
    raise
