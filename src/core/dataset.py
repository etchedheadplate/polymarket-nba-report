from abc import ABC, abstractmethod
from typing import Any


class DataSet(ABC):
    def __init__(self, query_rows: list[Any]):
        self._query_rows = query_rows

    @abstractmethod
    def process_data(self) -> Any: ...
