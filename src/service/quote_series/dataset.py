from decimal import Decimal
from typing import Any

from src.core.dataset import DataSet
from src.database.connection import sync_session_maker
from src.service.quote_series.schemas import HalftimeSegment, QuoteSeriesItem, UnderdogSegment
from src.service.repos import NBAGamesRepo
from src.service.schemas import PriceSnapshot
from src.service.utils import calculate_standard_deviation, normalize_prices


class QuoteSeriesDataSet(DataSet):
    def _extract_halftime_segment(self, item: QuoteSeriesItem) -> HalftimeSegment | None:
        guest_series = [(p.timestamp, p.guest_price) for p in item.price_series if p.guest_price is not None]
        host_series = [(p.timestamp, p.host_price) for p in item.price_series if p.host_price is not None]

        guest_series.sort()
        host_series.sort()

        all_series = guest_series + host_series
        all_series.sort()
        if not all_series:
            return None

        first_ts, last_ts = all_series[0][0], all_series[-1][0]
        if last_ts - first_ts < 15 * 60:
            return None

        center_ts = first_ts + (last_ts - first_ts) / 2
        halftime_duration = 15 * 60
        step_seconds = 60

        best_start, best_score = None, float("inf")

        for current_start in range(int(first_ts), int(last_ts - halftime_duration) + 1, step_seconds):
            current_end = current_start + halftime_duration

            guest_prices_window = [price for ts, price in guest_series if current_start <= ts <= current_end]
            host_prices_window = [price for ts, price in host_series if current_start <= ts <= current_end]

            vol_guest = calculate_standard_deviation(guest_prices_window)
            vol_host = calculate_standard_deviation(host_prices_window)

            distance_from_center = abs((current_start + current_end) / 2 - center_ts) / (last_ts - first_ts)
            score = vol_guest + vol_host + distance_from_center

            if score < best_score:
                best_score = score
                best_start = current_start

        if best_start is None:
            best_start = int(center_ts - halftime_duration / 2)

        return HalftimeSegment(start_ts=best_start, end_ts=best_start + halftime_duration)

    def _extract_underdog_segments(self, item: QuoteSeriesItem) -> list[UnderdogSegment]:
        prices = [
            (p.timestamp, p.guest_price, p.host_price)
            for p in item.price_series
            if p.guest_price is not None and p.host_price is not None
        ]

        if not prices:
            return []

        underdog_segments: list[UnderdogSegment] = []

        first_ts, first_guest, first_host = prices[0]
        current_team = item.guest_team if first_guest < first_host else item.host_team
        current_start_ts = first_ts
        current_min_price = first_guest if current_team == item.guest_team else first_host
        current_min_ts = first_ts

        for ts, guest_p, host_p in prices[1:]:
            new_team = item.guest_team if guest_p < host_p else item.host_team
            underdog_price = guest_p if current_team == item.guest_team else host_p

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
                current_min_price = guest_p if new_team == item.guest_team else host_p
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

    def _process_rows(self, rows: list[Any]) -> dict[int, QuoteSeriesItem]:
        all_quote_series: dict[int, QuoteSeriesItem] = {}

        for row in rows:
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

            if game_id not in all_quote_series:
                all_quote_series[game_id] = QuoteSeriesItem(
                    game_id=game_id,
                    game_date=game_date,
                    market_type=market_type,
                    guest_team=guest_team,
                    host_team=host_team,
                    guest_score=guest_score,
                    host_score=host_score,
                    price_series=[],
                )

            guest_price = normalize_prices(guest_buy, guest_sell)
            host_price = normalize_prices(host_buy, host_sell)

            if host_price and not guest_price:
                guest_price = Decimal("1.0") - host_price
            if guest_price and not host_price:
                host_price = Decimal("1.0") - guest_price

            all_quote_series[game_id].price_series.append(
                PriceSnapshot(
                    timestamp=timestamp,
                    guest_price=guest_price,
                    host_price=host_price,
                )
            )

        return all_quote_series

    def create_dataset(self) -> dict[int, QuoteSeriesItem]:
        with sync_session_maker() as session:
            rows = NBAGamesRepo().get_games(session=session, query=self._query)

        dataset = self._process_rows(rows)
        for game in dataset.values():
            game._halftime_seg = self._extract_halftime_segment(game)  # type: ignore
            game._underdog_segs = self._extract_underdog_segments(game)  # type: ignore

        return dataset
