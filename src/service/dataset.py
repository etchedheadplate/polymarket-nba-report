from decimal import Decimal
from typing import Any

import numpy as np

from src.core.dataset import DataSet
from src.database.connection import async_session_maker
from src.service.repos import NBAGamesRepo
from src.service.schemas import GameData, HalftimeSegment, PriceSnapshot, UnderdogSegment, WindowSegment


class GameSeriesData:
    def __init__(self, rows: list[Any]) -> None:
        self._rows = rows

    def process_rows(self) -> dict[int, GameData]:
        games_data_dict: dict[int, GameData] = {}

        for row in self._rows:
            (
                game_id,
                game_date,
                guest_team,
                host_team,
                guest_score,
                host_score,
                market_type,
                timestamp,
                guest_buy,
                guest_sell,
                host_buy,
                host_sell,
            ) = row

            if game_id not in games_data_dict:
                games_data_dict[game_id] = GameData(
                    game_id=game_id,
                    game_date=game_date,
                    market_type=market_type,
                    guest_team=guest_team,
                    host_team=host_team,
                    guest_score=guest_score,
                    host_score=host_score,
                    price_series=[],
                )

            games_data_dict[game_id].price_series.append(
                PriceSnapshot(
                    timestamp=timestamp,
                    guest_price=self.normalize_prices(guest_buy, guest_sell),
                    host_price=self.normalize_prices(host_buy, host_sell),
                )
            )

        return games_data_dict

    def extract_halftime_segment(self, game: GameData) -> HalftimeSegment | None:
        guest_series = [(p.timestamp, p.guest_price) for p in game.price_series if p.guest_price is not None]
        host_series = [(p.timestamp, p.host_price) for p in game.price_series if p.host_price is not None]

        all_series = guest_series + host_series
        if not all_series:
            return None

        all_series.sort(key=lambda p: p[0])
        first_ts = all_series[0][0]
        last_ts = all_series[-1][0]

        if last_ts - first_ts < 15 * 60:
            return None

        center_ts = first_ts + (last_ts - first_ts) / 2
        halftime_duration = 15 * 60
        step_seconds = 60

        prices_guest = np.array([float(price) for _, price in guest_series])
        prices_host = np.array([float(price) for _, price in host_series])
        ts_guest = np.array([ts for ts, _ in guest_series])
        ts_host = np.array([ts for ts, _ in host_series])

        best_start, best_score = None, float("inf")

        for current_start in range(int(first_ts), int(last_ts - halftime_duration) + 1, step_seconds):
            current_end = current_start + halftime_duration

            mask_guest = (ts_guest >= current_start) & (ts_guest <= current_end)
            mask_host = (ts_host >= current_start) & (ts_host <= current_end)

            vol_guest = np.nanstd(prices_guest[mask_guest]) if mask_guest.any() else 0
            vol_host = np.nanstd(prices_host[mask_host]) if mask_host.any() else 0

            distance_from_center = abs((current_start + current_end) / 2 - center_ts) / (last_ts - first_ts)
            score = vol_guest + vol_host + distance_from_center

            if score < best_score:
                best_score = score
                best_start = current_start

        if best_start is None:
            best_start = int(center_ts - halftime_duration / 2)

        return HalftimeSegment(start_ts=best_start, end_ts=best_start + halftime_duration)

    def extract_underdog_segments(self, game: GameData) -> list[UnderdogSegment]:
        prices = [
            (p.timestamp, p.guest_price, p.host_price)
            for p in game.price_series
            if p.guest_price is not None and p.host_price is not None
        ]

        if not prices:
            return []

        underdog_segments: list[UnderdogSegment] = []

        first_ts, first_guest, first_host = prices[0]
        current_team = game.guest_team if first_guest < first_host else game.host_team
        current_start_ts = first_ts
        current_min_price = first_guest if current_team == game.guest_team else first_host
        current_min_ts = first_ts

        for ts, guest_p, host_p in prices[1:]:
            new_team = game.guest_team if guest_p < host_p else game.host_team
            underdog_price = guest_p if current_team == game.guest_team else host_p

            if underdog_price < current_min_price:
                current_min_price = underdog_price
                current_min_ts = ts

            if new_team != current_team:
                underdog_segments.append(
                    UnderdogSegment(
                        team=current_team,
                        start_ts=current_start_ts,
                        end_ts=ts,
                        min_price=current_min_price,
                        min_ts=current_min_ts,
                    )
                )

                current_team = new_team
                current_start_ts = ts
                current_min_price = guest_p if new_team == game.guest_team else host_p
                current_min_ts = ts

        underdog_segments.append(
            UnderdogSegment(
                team=current_team,
                start_ts=current_start_ts,
                end_ts=prices[-1][0],
                min_price=current_min_price,
                min_ts=current_min_ts,
            )
        )

        return underdog_segments

    def extract_price_windows_segments(
        self, game: GameData, team: str, window: tuple[Decimal, Decimal]
    ) -> list[WindowSegment]:
        price_change_segments: list[WindowSegment] = []

        series: list[tuple[int, Decimal]] = []
        for p in game.price_series:
            price = p.guest_price if team == game.guest_team else p.host_price
            if price is not None:
                series.append((p.timestamp, price))

        in_segment = False
        start_ts = 0
        start_p = Decimal(0)
        window_start, window_end = window
        for ts, price in sorted(series):
            if not in_segment:
                if price <= window_start:
                    in_segment = True
                    start_ts = ts
                    start_p = price
            else:
                if price >= window_end:
                    price_change_segments.append(
                        WindowSegment(
                            team=team,
                            start_price=start_p,
                            start_ts=start_ts,
                            end_price=price,
                            end_ts=ts,
                        )
                    )
                    in_segment = False

        return price_change_segments

    @staticmethod
    def normalize_prices(buy: Decimal | None, sell: Decimal | None) -> Decimal | None:
        if buy is not None and sell is not None:
            return (buy + sell) / 2
        return buy or sell


class QuoteSeriesDataSet(DataSet):
    def __init__(self, query: Any) -> None:
        super().__init__(query)

    async def _query_database(self) -> list[Any]:
        async with async_session_maker() as session:
            return await NBAGamesRepo().get_game_series(session, self._query)

    async def create_dataset(self) -> dict[int, GameData]:
        rows = await self._query_database()
        series = GameSeriesData(rows)
        dataset = series.process_rows()

        for game in dataset.values():
            game._halftime_seg = series.extract_halftime_segment(game)  # type: ignore[reportPrivateUsage]
            game._underdog_segs = series.extract_underdog_segments(game)  # type: ignore[reportPrivateUsage]

        return dataset


class PriceWindowDataSet(DataSet):
    def __init__(self, query: Any) -> None:
        super().__init__(query)

    async def _query_database(self) -> list[Any]:
        async with async_session_maker() as session:
            return await NBAGamesRepo().get_game_series(session, self._query)

    async def create_dataset(self) -> dict[int, GameData]:
        rows = await self._query_database()
        series = GameSeriesData(rows)
        dataset = series.process_rows()

        for game in dataset.values():
            start_price = self._query.start_price
            end_price = self._query.end_price
            team = self._query.team.name

            price_change_segments = series.extract_price_windows_segments(
                game=game, team=team, window=(start_price, end_price)
            )
            game._price_change_segs = price_change_segments  # type: ignore[reportPrivateUsage]

        return dataset
