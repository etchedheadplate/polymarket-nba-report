from pathlib import Path

from src.core.summary import Summary
from src.service.reports.quote_series.schemas import QuoteSeriesItem, QuoteSeriesQuery


class QuoteSeriesSummary(Summary):
    def __init__(self, summary_title: str, query: QuoteSeriesQuery, dataset: dict[int, QuoteSeriesItem]) -> None:
        super().__init__(summary_title=summary_title, query=query, dataset=dataset)

    def _make_data_summary(self) -> Path:
        summary_name = f"dummy.{self._summary_ext}"
        summary_path = self._summary_dir / summary_name

        report_blocks = [
            "future report",
        ]

        self._report_text = "\n".join(report_blocks)
        return summary_path
