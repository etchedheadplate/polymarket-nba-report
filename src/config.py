from pathlib import Path
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    OUTPUT_DIR: Path = Path("reports")

    FONT_PATH: Path | None = None
    BG_QUOTE_SERIES_PATH: Path | None = None
    BG_PRICE_WINDOW_PATH: Path | None = None

    @field_validator("FONT_PATH", "BG_QUOTE_SERIES_PATH", "BG_PRICE_WINDOW_PATH", mode="before")
    @classmethod
    def empty_str_to_none(cls, v: str):
        if v == "":
            return None
        return v

    DB_NAME: str = "polymarket_nba_oracle"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASS: str = "postgres"

    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "guest"
    RABBITMQ_PASSWORD: str = "guest"
    RABBITMQ_VHOST: str = "/"

    EXCHANGE_NAME: str = "polymarket.nba"
    QUEUE_TG_BOT: str = "tg_bot"
    QUEUE_ORACLE: str = "oracle"
    QUEUE_REPORT: str = "report"
    RK_REQUEST: str = "request"
    RK_RESPONSE: str = "response"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()  # pyright: ignore[reportCallIssue]
