from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_NAME: str
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str

    SHARED_DIR: Path
    TEAM_LOGO_DIR: Path

    VISUALS_FONT_PATH: Path
    BACKGROUND_QUOTE_SERIES_PATH: Path
    BACKGROUND_PRICE_WINDOW_PATH: Path

    RABBITMQ_HOST: str
    RABBITMQ_PORT: int
    RABBITMQ_USER: str
    RABBITMQ_PASSWORD: str
    RABBITMQ_VHOST: str

    EXCHANGE_NAME: str
    QUEUE_TGBOT: str
    QUEUE_ORACLE: str
    QUEUE_REPORT: str
    RK_REQUEST: str
    RK_RESPONSE: str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()  # type: ignore[call-arg]
