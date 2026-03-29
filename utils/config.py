from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    bot_token: str = Field(alias="BOT_TOKEN")
    schedule_file: str = Field(alias="SCHEDULE_FILE")
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

class MessageText(BaseSettings):
    schedule_today: str = "🗓 на сегодня"
    schedule_tomorrow: str = "🗓 на завтра"
    current_lesson: str = "▶️ Сейчас"
    next_lesson: str = "⏭ Следующая"
    other: str = "Прочее"

messages = MessageText()
settings = Settings()
