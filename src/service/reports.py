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
