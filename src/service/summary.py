from pathlib import Path

from src.core.summary import Summary
from src.service.schemas import GameData, ReportQuery


class QuoteSeriesSummary(Summary):
    def __init__(self, query: ReportQuery, dataset: dict[int, GameData]) -> None:
        super().__init__(query=query, dataset=dataset)

    def _make_data_summary(self) -> Path:
        return Path()


class PriceWindowSummary(Summary):
    def __init__(self, query: ReportQuery, dataset: dict[int, GameData]) -> None:
        super().__init__(query=query, dataset=dataset)

    def _make_data_summary(self) -> Path:
        return Path()
