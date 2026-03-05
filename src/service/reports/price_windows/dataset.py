from decimal import Decimal
from typing import Any

from src.core.dataset import DataSet
from src.database.connection import sync_session_maker
from src.service.domain import NBATeamSide
from src.service.reports.price_windows.schemas import PriceWindowItem, WindowSegment
from src.service.reports.schemas import PriceSnapshot
from src.service.reports.utils import normalize_prices
from src.service.repos import NBAGamesRepo


class PriceWindowDataSet(DataSet):
    def _build_price_window_segments(
        self,
        series: list[tuple[int, Decimal]],
        window_start: Decimal,
        window_end: Decimal,
    ) -> list[WindowSegment]:

        segments: list[WindowSegment] = []

        in_segment = False
        start_ts = 0
        start_price = Decimal(0)

        for ts, price in series:
            if not in_segment:
                if price <= window_start:
                    in_segment = True
                    start_ts = ts
                    start_price = price
            else:
                if price >= window_end:
                    segments.append(
                        WindowSegment(
                            start_price=start_price,
                            start_ts=start_ts,
                            end_price=price,
                            end_ts=ts,
                        )
                    )
                    in_segment = False

        return segments

    def _extract_price_window_segments(
        self,
        item: PriceWindowItem,
        window_start: Decimal,
        window_end: Decimal,
    ) -> dict[NBATeamSide, list[WindowSegment]]:

        series_guest: list[tuple[int, Decimal]] = []
        series_host: list[tuple[int, Decimal]] = []

        for p in item.price_series:
            if p.guest_price is not None:
                series_guest.append((p.timestamp, p.guest_price))
            if p.host_price is not None:
                series_host.append((p.timestamp, p.host_price))

        series_guest.sort()
        series_host.sort()

        return {
            NBATeamSide.GUEST: self._build_price_window_segments(series_guest, window_start, window_end),
            NBATeamSide.HOST: self._build_price_window_segments(series_host, window_start, window_end),
        }

    def _process_rows(self, rows: list[Any]) -> dict[int, PriceWindowItem]:
        all_price_windows: dict[int, PriceWindowItem] = {}
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
            if game_id not in all_price_windows:
                all_price_windows[game_id] = PriceWindowItem(
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

            all_price_windows[game_id].price_series.append(
                PriceSnapshot(
                    timestamp=timestamp,
                    guest_price=guest_price,
                    host_price=host_price,
                )
            )
        return all_price_windows

    def create_dataset(self) -> dict[int, PriceWindowItem]:
        with sync_session_maker() as session:
            rows = NBAGamesRepo().get_games_with_prices(session=session, query=self._query, team_conditions=False)

        start, end = self._query.window_start, self._query.window_end
        dataset = self._process_rows(rows=rows)
        for game in dataset.values():
            game._window_segs = self._extract_price_window_segments(  # pyright: ignore[reportPrivateUsage]
                item=game, window_start=start, window_end=end
            )

        return dataset
