from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    bot_token: str = Field(alias="BOT_TOKEN")
    admin_id: int = Field(alias="ADMIN_ID")
    schedule_file: str = Field(default="data/schedule.json", alias="SCHEDULE_FILE")
    database_file: str = Field(default="data/database.db", alias="DATABASE_FILE")
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

class MessageText(BaseSettings):
    schedule_today: str = "🗓 на сегодня"
    schedule_tomorrow: str = "🗓 на завтра"
    current_lesson: str = "▶️ Сейчас"
    next_lesson: str = "⏭ Следующая"
    choose_day: str = "📅 Выбрать день"
    other: str = "Прочее"

messages = MessageText()
settings = Settings()
