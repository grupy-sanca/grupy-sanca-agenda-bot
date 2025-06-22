from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    TELEGRAM_BOT_TOKEN: str
    MEETUP_GROUP_URL: str
    GROUP_CHAT_ID: str
    GROUP_CHAT_TOPIC_ID: str | None = None
    ADMINS: list[int] | None = None
    TIMEOUT_SECONDS: int | None = 60
    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
