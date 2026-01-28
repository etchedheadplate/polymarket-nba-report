from decimal import Decimal
from typing import Any

from src.core.reports import Report
from src.database.connection import async_session_maker
from src.service.repos import NBAGamesRepo
from src.service.schemas import GamesSeriesPriceResponse, GamesSeriesQuery, GamesSeriesResponse
from src.service.summary import GamesSummary
from src.service.visuals import GamesPlot


class GamesReport(Report):
    _visuals_cls = GamesPlot
    _summary_cls = GamesSummary

    def __init__(self, query: GamesSeriesQuery) -> None:
        super().__init__(query)

    async def _query_database(self) -> list[Any]:
        async with async_session_maker() as session:
            return await NBAGamesRepo().get_games_series(session, self.query)

    def _process_data(self, query_rows: list[Any]) -> dict[int, GamesSeriesResponse]:
        games_data_dict: dict[int, GamesSeriesResponse] = {}

        def normalize_prices(buy: Decimal | None, sell: Decimal | None) -> Decimal | None:
            if buy is not None and sell is not None:
                return (buy + sell) / 2
            return buy or sell

        for (
            game_id,
            game_date,
            g_team,
            h_team,
            g_score,
            h_score,
            market_type,
            ts,
            g_buy,
            g_sell,
            h_buy,
            h_sell,
        ) in query_rows:
            game_entry = games_data_dict.setdefault(
                game_id,
                GamesSeriesResponse(
                    game_id=game_id,
                    game_date=game_date,
                    market_type=market_type,
                    guest_team=g_team,
                    host_team=h_team,
                    guest_score=g_score,
                    host_score=h_score,
                    prices=[],
                ),
            )

            game_entry.prices.append(
                GamesSeriesPriceResponse(
                    timestamp=ts,
                    guest_price=normalize_prices(g_buy, g_sell),
                    host_price=normalize_prices(h_buy, h_sell),
                )
            )

        return games_data_dict
