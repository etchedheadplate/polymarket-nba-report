from typing import Any

from src.core.reports import Report
from src.database.connection import async_session_maker
from src.service.dataset import GameDataSet
from src.service.repos import NBAGamesRepo
from src.service.schemas import GameSeriesQuery
from src.service.summary import QuoteSeriesSummary
from src.service.visuals import QuoteSeriesPlot


class GameSeriesReport(Report):
    def __init__(self, query: GameSeriesQuery) -> None:
        super().__init__(query)

    async def _query_database(self) -> list[Any]:
        async with async_session_maker() as session:
            return await NBAGamesRepo().get_games_series(session, self.query)


class QuoteSeriesReport(GameSeriesReport):
    _handler_cls = GameDataSet
    _visuals_cls = QuoteSeriesPlot
    _summary_cls = QuoteSeriesSummary

    def __init__(self, query: GameSeriesQuery) -> None:
        super().__init__(query)
