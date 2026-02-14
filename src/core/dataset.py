from abc import ABC, abstractmethod
from typing import Any


class DataSet(ABC):
    def __init__(self, query: Any):
        self._query = query

    @abstractmethod
    async def create_dataset(self) -> Any: ...
