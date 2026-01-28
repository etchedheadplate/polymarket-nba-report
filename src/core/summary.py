import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from src.config import settings


class Summary(ABC):
    _shared_dir = settings.SHARED_DIR
    _output_dir: str

    def __init__(self, input_data: Any) -> None:
        self._input_data = input_data
        os.makedirs(self._shared_dir, exist_ok=True)

    @abstractmethod
    def _make_data_summary(self) -> Path: ...

    def create_summary(self) -> Path:
        summary_path = self._make_data_summary()
        return summary_path
