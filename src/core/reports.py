from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from src.core.summary import Summary
from src.core.visuals import Visuals
from src.logger import logger


class Report(ABC):
    _visuals_cls: type[Visuals]
    _summary_cls: type[Summary]

    def __init__(self, query: Any) -> None:
        self.query = query
        self.visuals: list[Path] = []
        self.summary: Path = Path()

    @abstractmethod
    async def _query_database(self) -> list[Any]: ...

    @abstractmethod
    def _process_data(self, query_rows: list[Any]) -> Any: ...

    def _create_visuals(self, procesesed_items: Any) -> None:
        visuals_processor = self._visuals_cls(procesesed_items)
        self.visuals = visuals_processor.create_visuals()

    def _create_summary(self, procesesed_items: Any) -> None:
        summary_processor = self._summary_cls(procesesed_items)
        self.summary = summary_processor.create_summary()

    async def make_report(self) -> Any:
        query_rows = await self._query_database()
        procesesed_items = self._process_data(query_rows)
        logger.debug("Processed %s items from %s rows", len(procesesed_items), len(query_rows))
        self._create_visuals(procesesed_items)
        self._create_summary(procesesed_items)
