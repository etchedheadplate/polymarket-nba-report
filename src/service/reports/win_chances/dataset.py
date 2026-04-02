from decimal import Decimal
from typing import Any

from src.core.dataset import DataSet
from src.database.connection import sync_session_maker
from src.service.reports.schemas import PriceSnapshot
from src.service.reports.utils import normalize_prices
from src.service.reports.win_chances.schemas import WinChancesItem
from src.service.repos import NBAGamesRepo


class WinChancesDataSet(DataSet):
    def _process_rows(self, rows: list[Any]) -> dict[int, WinChancesItem]:
        all_games: dict[int, WinChancesItem] = {}
        for row in rows:
            (
                game_id,
                _,
                guest_team,
                host_team,
                _,
                _,
                _,
                timestamp,
                guest_buy,
                guest_sell,
                host_buy,
                host_sell,
            ) = row
            if game_id not in all_games:
                all_games[game_id] = WinChancesItem(
                    guest_team=guest_team,
                    host_team=host_team,
                    price_series=[],
                )

            guest_price = normalize_prices(guest_buy, guest_sell)
            host_price = normalize_prices(host_buy, host_sell)

            if host_price and not guest_price:
                guest_price = Decimal("1.0") - host_price
            if guest_price and not host_price:
                host_price = Decimal("1.0") - guest_price

            all_games[game_id].price_series.append(
                PriceSnapshot(
                    timestamp=timestamp,
                    guest_price=guest_price,
                    host_price=host_price,
                )
            )
        return all_games

    def create_dataset(self) -> dict[int, WinChancesItem]:
        with sync_session_maker() as session:
            rows = NBAGamesRepo().get_games_with_prices(session=session, query=self._query, team_conditions=False)

        return self._process_rows(rows=rows)
