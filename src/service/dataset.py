from typing import Any

from src.core.dataset import DataSet
from src.database.connection import async_session_maker
from src.service.processor import GameProcessor
from src.service.repos import NBAGamesRepo
from src.service.schemas import GameData


class QuoteSeriesDataSet(DataSet):
    _processor_cls = GameProcessor

    def __init__(self, query: Any) -> None:
        super().__init__(query)

    async def query_database(self) -> list[Any]:
        async with async_session_maker() as session:
            return await NBAGamesRepo().get_games_series(session, self._query)

    async def create_dataset(self) -> dict[int, GameData]:
        rows = await self.query_database()
        processor = self._processor_cls(rows)
        game_series = processor.create_data_dict()

        for _, game in game_series.items():
            halftime_segment = processor.extract_halftime_segment(game_data=game)
            game._halftime_seg = halftime_segment  # type: ignore[reportPrivateUsage]

            underdog_segments = processor.extract_underdog_segments(game_data=game)
            game._underdog_segs = underdog_segments  # type: ignore[reportPrivateUsage]

        return game_series


class PriceWindowDataSet(DataSet):
    _processor_cls = GameProcessor

    def __init__(self, query: Any) -> None:
        super().__init__(query)

    async def query_database(self) -> list[Any]:
        async with async_session_maker() as session:
            return await NBAGamesRepo().get_games_series(session, self._query)

    async def create_dataset(self) -> dict[int, GameData]:
        rows = await self.query_database()
        processor = self._processor_cls(rows)
        game_series = processor.create_data_dict()

        for _, game in game_series.items():
            start_price = self._query.start_price
            end_price = self._query.end_price
            team_name = self._query.team.name

            price_change_segments = processor.extract_price_change_segments(
                game_data=game, start_price=start_price, end_price=end_price, team_name=team_name
            )
            game._price_change_segs = price_change_segments  # type: ignore[reportPrivateUsage]

        return game_series
