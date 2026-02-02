from src.core.reports import Report
from src.service.dataset import GameSeriesDataSet
from src.service.schemas import GameSeriesQuery
from src.service.summary import GameSeriesSummary
from src.service.visuals import GameSeriesPlot


class GameSeriesReport(Report):
    _dataset_cls = GameSeriesDataSet
    _visuals_cls = GameSeriesPlot
    _summary_cls = GameSeriesSummary

    def __init__(self, query: GameSeriesQuery) -> None:
        super().__init__(query)
