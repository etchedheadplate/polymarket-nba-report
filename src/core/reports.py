from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from src.core.summary import Summary
from src.core.visuals import Visuals


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
    def _process_data(self, raw_data: list[Any]) -> Any: ...

    def _create_visuals(self, procseesed_data: Any) -> None:
        visuals_processor = self._visuals_cls(procseesed_data)
        self.visuals = visuals_processor.create_visuals()

    def _create_summary(self, procseesed_data: Any) -> None:
        summary_processor = self._summary_cls(procseesed_data)
        self.summary = summary_processor.create_summary()

    async def make_report(self) -> Any:
        raw_data = await self._query_database()
        procseesed_data = self._process_data(raw_data)
        self._create_visuals(procseesed_data)
        self._create_summary(procseesed_data)
