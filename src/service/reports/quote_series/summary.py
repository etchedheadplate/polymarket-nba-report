from pathlib import Path

from src.core.summary import Summary
from src.service.reports.quote_series.schemas import QuoteSeriesItem, QuoteSeriesQuery


class QuoteSeriesSummary(Summary):
    _file_output_dir = "quote_series"

    def __init__(self, query: QuoteSeriesQuery, dataset: dict[int, QuoteSeriesItem]) -> None:
        super().__init__(query=query, dataset=dataset)

    def _make_data_summary(self) -> Path:
        report_dir = self._path_shared_dir / self._file_output_dir
        report_path = report_dir / f"dummy.{self._report_ext}"

        report_blocks = [
            f"future {self._file_output_dir} report",
        ]

        self._report_text = "\n".join(report_blocks)
        return report_path
