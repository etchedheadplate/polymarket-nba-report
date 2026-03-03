from typing import TypedDict

from src.core.reports import Report
from src.service.price_windows import (
    PriceWindowChart,
    PriceWindowDataSet,
    PriceWindowQuery,
    PriceWindowSummary,
)
from src.service.quote_series import (
    QuoteSeriesDataSet,
    QuoteSeriesPlot,
    QuoteSeriesQuery,
    QuoteSeriesSummary,
)
from src.service.schemas import ReportQuery


class QuoteSeriesReport(Report):
    _dataset_cls = QuoteSeriesDataSet
    _visuals_cls = QuoteSeriesPlot
    _summary_cls = QuoteSeriesSummary

    def __init__(self, query: QuoteSeriesQuery) -> None:
        super().__init__(query)


class PriceWindowReport(Report):
    _dataset_cls = PriceWindowDataSet
    _visuals_cls = PriceWindowChart
    _summary_cls = PriceWindowSummary

    def __init__(self, query: PriceWindowQuery) -> None:
        super().__init__(query)


class ReportMapping(TypedDict):
    report: type[Report]
    query: type[ReportQuery]


_report_map: dict[str, ReportMapping] = {
    "price_windows": {"report": PriceWindowReport, "query": PriceWindowQuery},
    "quote_series": {"report": QuoteSeriesReport, "query": QuoteSeriesQuery},
}


def select_report(name: str) -> tuple[type[Report], type[ReportQuery]]:
    mapping = _report_map.get(name)
    if mapping is None:
        raise ValueError(f"Unknown report: {name}")
    return mapping["report"], mapping["query"]
