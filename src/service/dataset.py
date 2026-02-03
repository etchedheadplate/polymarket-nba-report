from decimal import Decimal
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
            halftime_segment = processor.extract_halftime_segment(game)
            game._halftime_ts = halftime_segment  # type: ignore[reportPrivateUsage]

            underdog_segments = processor.extract_underdog_segments(game)
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
            price_change_segments = processor.extract_price_change_segments(
                game, start_price=Decimal("0.1"), end_price=Decimal("0.3")
            )
            print(_, price_change_segments)

        return game_series
