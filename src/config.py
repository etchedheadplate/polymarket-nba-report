from pathlib import Path
from typing import Any

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_NAME: str
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str

    SHARED_DIR: Path

    PLOT_FONT_PATH: Path
    PLOT_BACKGROUND_PATH: Path
    PLOT_CONFIG: dict[str, Any] = {
        "font.family": "Montserrat",
        "text.color": "#e9ecef",
        "figure.facecolor": "#e9ecef",
        "axes.facecolor": "#e9ecef",
        "axes.labelcolor": "#e9ecef",
        "axes.titlecolor": "#e9ecef",
        "axes.edgecolor": "#bbbbbb",
        "axes.labelsize": 10,
        "axes.titlesize": 20,
        "xtick.labelsize": 12,
        "ytick.labelsize": 12,
        "xtick.color": "#e9ecef",
        "ytick.color": "#e9ecef",
        "axes.grid": True,
        "grid.color": "#f8f9fa",
        "grid.linestyle": "-",
        "grid.linewidth": 1,
        "grid.alpha": 0.6,
    }

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()  # type: ignore[call-arg]
