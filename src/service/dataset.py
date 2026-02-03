from decimal import Decimal
from typing import Any

import numpy as np

from src.core.dataset import DataSet
from src.database.connection import async_session_maker
from src.service.repos import NBAGamesRepo
from src.service.schemas import GameSeries, PriceSnapshot, UnderdogSegment


class GameSeriesDataSet(DataSet):
    def __init__(self, query: Any) -> None:
        super().__init__(query)

    async def query_database(self) -> None:
        async with async_session_maker() as session:
            self._rows = await NBAGamesRepo().get_games_series(session, self._query)

    def _detect_halftime_segment(self, game_data: GameSeries) -> tuple[int, int] | None:
        guest_series = [(p.timestamp, p.guest_price) for p in game_data.price_series if p.guest_price is not None]
        host_series = [(p.timestamp, p.host_price) for p in game_data.price_series if p.host_price is not None]

        all_series = guest_series + host_series
        if not all_series:
            return None

        all_series.sort(key=lambda p: p[0])
        timestamps = np.array([ts for ts, _ in all_series])
        prices_guest = np.array([float(guest_price) for _, guest_price in guest_series])
        prices_host = np.array([float(host_price) for _, host_price in host_series])

        step_seconds = 60
        halftime_duration = 15 * 60

        first_ts, last_ts = timestamps[0], timestamps[-1]
        center_ts = first_ts + (last_ts - first_ts) / 2

        best_start, best_score = None, float("inf")
        current_start = first_ts

        while current_start + halftime_duration <= last_ts:
            current_end = current_start + halftime_duration
            mask_guest = (np.array([ts for ts, _ in guest_series]) >= current_start) & (
                np.array([ts for ts, _ in guest_series]) <= current_end
            )
            mask_host = (np.array([ts for ts, _ in host_series]) >= current_start) & (
                np.array([ts for ts, _ in host_series]) <= current_end
            )

            vol_guest = np.nanstd(prices_guest[mask_guest]) if mask_guest.any() else 0
            vol_host = np.nanstd(prices_host[mask_host]) if mask_host.any() else 0
            vol_total = vol_guest + vol_host

            distance_from_center = abs((current_start + current_end) / 2 - center_ts) / (last_ts - first_ts)
            score = vol_total + distance_from_center

            if score < best_score:
                best_score = score
                best_start = current_start

            current_start += step_seconds

        if best_start is None:
            best_start = center_ts - halftime_duration / 2

        return int(best_start), int(best_start + halftime_duration)

    def _extract_underdog_segments(self, game_data: GameSeries) -> list[UnderdogSegment]:
        prices = [p for p in game_data.price_series if p.guest_price is not None and p.host_price is not None]
        if not prices:
            return []

        guest_team = game_data.guest_team
        host_team = game_data.host_team

        first = prices[0]

        if first.guest_price is None or first.host_price is None:
            return []

        current_team = guest_team if first.guest_price < first.host_price else host_team
        current_start_ts = first.timestamp
        current_min_price = first.guest_price if current_team == guest_team else first.host_price
        current_min_ts = first.timestamp

        segments: list[UnderdogSegment] = []

        for p in prices[1:]:
            guest_p = p.guest_price
            host_p = p.host_price
            if guest_p is None or host_p is None:
                continue

            new_team = guest_team if guest_p < host_p else host_team
            underdog_price = guest_p if current_team == guest_team else host_p

            if underdog_price < current_min_price:
                current_min_price = underdog_price
                current_min_ts = p.timestamp

            if new_team != current_team:
                segments.append(
                    UnderdogSegment(
                        team=current_team,
                        start_ts=current_start_ts,
                        end_ts=p.timestamp,
                        min_price=current_min_price,
                        min_ts=current_min_ts,
                    )
                )

                current_team = new_team
                current_start_ts = p.timestamp
                current_min_price = guest_p if new_team == guest_team else host_p
                current_min_ts = p.timestamp

        segments.append(
            UnderdogSegment(
                team=current_team,
                start_ts=current_start_ts,
                end_ts=prices[-1].timestamp,
                min_price=current_min_price,
                min_ts=current_min_ts,
            )
        )

        return segments

    def process_data(self) -> dict[int, GameSeries]:
        games_data_dict: dict[int, GameSeries] = {}

        def normalize_prices(buy: Decimal | None, sell: Decimal | None) -> Decimal | None:
            if buy is not None and sell is not None:
                return (buy + sell) / 2
            return buy or sell

        for (
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
        ) in self._rows:
            game_entry = games_data_dict.setdefault(
                game_id,
                GameSeries(
                    game_id=game_id,
                    game_date=game_date,
                    market_type=market_type,
                    guest_team=guest_team,
                    host_team=host_team,
                    guest_score=guest_score,
                    host_score=host_score,
                    price_series=[],
                ),
            )

            game_entry.price_series.append(
                PriceSnapshot(
                    timestamp=timestamp,
                    guest_price=normalize_prices(guest_buy, guest_sell),
                    host_price=normalize_prices(host_buy, host_sell),
                )
            )

        for _, game_data in games_data_dict.items():
            underdog_segments = self._extract_underdog_segments(game_data)
            game_data._underdog_segs = underdog_segments  # type: ignore[reportPrivateUsage]

            halftime_segment = self._detect_halftime_segment(game_data)
            game_data._halftime_ts = halftime_segment  # type: ignore[reportPrivateUsage]

        return games_data_dict
