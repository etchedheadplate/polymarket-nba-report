from abc import ABC, abstractmethod
from typing import Any


class DataSet(ABC):
    def __init__(self, query: Any):
        self._query = query

    @abstractmethod
    def _process_rows(self, rows: list[Any]) -> dict[int, Any]: ...

    @abstractmethod
    async def create_dataset(self) -> dict[int, Any]: ...
