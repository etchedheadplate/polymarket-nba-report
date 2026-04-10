from typing import TypedDict

from src.core.reports import Report
from src.service.reports import price_windows, quote_series
from src.service.reports.schemas import ReportQuery


class QuoteSeriesReport(Report):
    report_title = "quote_series"
    _dataset_cls = quote_series.QuoteSeriesDataSet
    _visuals_cls = quote_series.QuoteSeriesPlot
    _summary_cls = quote_series.QuoteSeriesSummary

    def __init__(self, query: quote_series.QuoteSeriesQuery) -> None:
        super().__init__(title=self.report_title, query=query)


class PriceWindowReport(Report):
    report_title: str = "price_windows"
    _dataset_cls = price_windows.PriceWindowDataSet
    _visuals_cls = price_windows.PriceWindowChart
    _summary_cls = price_windows.PriceWindowSummary

    def __init__(self, query: price_windows.PriceWindowQuery) -> None:
        super().__init__(title=self.report_title, query=query)


class ReportMapping(TypedDict):
    report: type[Report]
    query: type[ReportQuery]


_report_map: dict[str, ReportMapping] = {
    "price_windows": {"report": PriceWindowReport, "query": price_windows.PriceWindowQuery},
    "quote_series": {"report": QuoteSeriesReport, "query": quote_series.QuoteSeriesQuery},
}


def select_report(name: str) -> tuple[type[Report], type[ReportQuery]]:
    mapping = _report_map.get(name)
    if mapping is None:
        raise ValueError(f"Unknown report: {name}")
    return mapping["report"], mapping["query"]
