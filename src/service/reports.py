from src.core.reports import Report
from src.service.dataset import PriceWindowDataSet, QuoteSeriesDataSet
from src.service.schemas import PriceWindowQuery, QuoteSeriesQuery
from src.service.summary import PriceWindowSummary, QuoteSeriesSummary
from src.service.visuals import PriceWindowChart, QuoteSeriesPlot


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
