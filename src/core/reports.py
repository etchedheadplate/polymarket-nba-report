from abc import ABC
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

    def _create_dataset(self) -> Any:
        dataset_processor = self._dataset_cls(self.query)
        return dataset_processor.create_dataset()

    def _create_visuals(self, dataset: Any) -> None:
        visuals_processor = self._visuals_cls(query=self.query, dataset=dataset)
        self.visuals = visuals_processor.create_visuals()

    def _create_summary(self, dataset: Any) -> None:
        summary_processor = self._summary_cls(query=self.query, dataset=dataset)
        self.summary = summary_processor.create_summary()

    def make_report(self) -> Any:
        dataset = self._create_dataset()
        logger.debug("report %s: processed %s items", self.__class__.__name__, len(dataset))
        self._create_visuals(dataset)
        self._create_summary(dataset)
