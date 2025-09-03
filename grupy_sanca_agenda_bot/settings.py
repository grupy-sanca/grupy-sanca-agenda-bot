from pydantic_settings import BaseSettings, SettingsConfigDict

from grupy_sanca_agenda_bot.constants import EventExtractorEnum


class Settings(BaseSettings):
    TELEGRAM_BOT_TOKEN: str
    URL: str
    EVENT_EXTRACTOR: EventExtractorEnum = EventExtractorEnum.open_event
    GROUP_CHAT_ID: str
    GROUP_CHAT_TOPIC_ID: str | None = None
    ADMINS: list[int] | None = None
    TIMEOUT_SECONDS: int | None = 60
    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
