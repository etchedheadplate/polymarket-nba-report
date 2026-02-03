from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_NAME: str
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str

    SHARED_DIR: Path

    VISUALS_FONT_PATH: Path
    BACKGROUND_QUOTE_SERIES_PATH: Path
    BACKGROUND_PRICE_WINDOW_PATH: Path

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()  # type: ignore[call-arg]
