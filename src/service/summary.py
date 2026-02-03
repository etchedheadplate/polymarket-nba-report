from pathlib import Path

from src.core.summary import Summary
from src.service.schemas import GameData


class QuoteSeriesSummary(Summary):
    def __init__(self, games_data: dict[int, GameData]) -> None:
        super().__init__(games_data)

    def _make_data_summary(self) -> Path:
        return Path()


class PriceWindowSummary(Summary):
    def __init__(self, games_data: dict[int, GameData]) -> None:
        super().__init__(games_data)

    def _make_data_summary(self) -> Path:
        return Path()
