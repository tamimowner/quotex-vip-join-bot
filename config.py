from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    BOT_TOKEN: str
    ADMIN_IDS: str = ""
    VIP_GROUP_ID: int

    AFFILIATE_LINK_BASE: str = "https://qxbroker.com/sign-up/?lid=1476468&click_id={click_id}&site_id={site_id}"
    SITE_ID: str = "1"

    DATABASE_URL: str

    POSTBACK_SECRET: str = ""
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    DEFAULT_LANGUAGE: str = "bn"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def admin_ids(self) -> List[int]:
        if not self.ADMIN_IDS:
            return []
        return [int(x.strip()) for x in self.ADMIN_IDS.split(",") if x.strip()]


settings = Settings()
