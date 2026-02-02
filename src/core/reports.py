from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from src.core.dataset import DataSet
from src.core.summary import Summary
from src.core.visuals import Visuals
from src.logger import logger


class Report(ABC):
    _dataset_cls: type[DataSet]
    _visuals_cls: type[Visuals]
    _summary_cls: type[Summary]

    def __init__(self, query: Any) -> None:
        self.query = query
        self.visuals: list[Path] = []
        self.summary: Path = Path()

    @abstractmethod
    async def _query_database(self) -> list[Any]: ...

    def _prepare_data(self, query_rows: list[Any]) -> Any:
        dataset_processor = self._dataset_cls(query_rows)
        return dataset_processor.process_data()

    def _create_visuals(self, procesesed_items: Any) -> None:
        visuals_processor = self._visuals_cls(procesesed_items)
        self.visuals = visuals_processor.create_visuals()

    def _create_summary(self, procesesed_items: Any) -> None:
        summary_processor = self._summary_cls(procesesed_items)
        self.summary = summary_processor.create_summary()

    async def make_report(self) -> Any:
        query_rows = await self._query_database()
        dataset = self._prepare_data(query_rows)
        logger.debug("Processed %s items from %s rows", len(dataset), len(query_rows))
        self._create_visuals(dataset)
        self._create_summary(dataset)
