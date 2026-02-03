from typing import Any

from src.core.dataset import DataSet
from src.database.connection import async_session_maker
from src.service.processor import GameProcessor
from src.service.repos import NBAGamesRepo
from src.service.schemas import GameSeries


class GameSeriesDataSet(DataSet):
    _processor_cls = GameProcessor

    def __init__(self, query: Any) -> None:
        super().__init__(query)

    async def query_database(self) -> None:
        async with async_session_maker() as session:
            self._rows = await NBAGamesRepo().get_games_series(session, self._query)

    async def create_dataset(self) -> dict[int, GameSeries]:
        await self.query_database()
        processor = self._processor_cls(self._query, self._rows)
        game_series = processor.create_data_dict()

        for _, game in game_series.items():
            halftime_segment = processor.extract_halftime_segment(game)
            game._halftime_ts = halftime_segment  # type: ignore[reportPrivateUsage]
            underdog_segments = processor.extract_underdog_segments(game)
            game._underdog_segs = underdog_segments  # type: ignore[reportPrivateUsage]

        return game_series
