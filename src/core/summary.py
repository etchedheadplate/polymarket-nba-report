import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from src.config import settings


class Summary(ABC):
    _path_shared_dir: Path = settings.SHARED_DIR
    _file_output_dir: str
    _report_ext: str = "md"

    def __init__(self, query: Any, dataset: Any) -> None:
        self._query = query
        self._dataset = dataset
        self._report_text = ""
        os.makedirs(self._path_shared_dir / self._file_output_dir, exist_ok=True)

    @abstractmethod
    def _make_data_summary(self) -> Path: ...

    def create_summary(self) -> Path:
        summary_path = self._make_data_summary()
        with open(summary_path, "w") as f:
            f.write(self._report_text)
        return summary_path
