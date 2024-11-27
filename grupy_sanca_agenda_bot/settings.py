from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    TELEGRAM_BOT_TOKEN: str
    MEETUP_GROUP_URL: str
    GROUP_CHAT_ID: str
    ADMINS: list[int] | None = None
    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
