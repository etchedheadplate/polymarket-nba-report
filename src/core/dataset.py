from abc import ABC, abstractmethod
from typing import Any


class DataSet(ABC):
    def __init__(self, query: Any):
        self._query = query
        self._rows: list[Any] = []

    @abstractmethod
    async def query_database(self) -> None: ...

    @abstractmethod
    def process_data(self) -> Any: ...
