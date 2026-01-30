from datetime import datetime
from decimal import Decimal
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from src.config import settings
from src.core.visuals import Chart, Plot
from src.logger import logger
from src.service.domain import NBATeamColor
from src.service.schemas import GameSeriesResponse


class QuoteSeriesPlot(Plot):
    _image_bg_path = settings.BACKGROUND_QUOTE_SERIES_PATH

    def __init__(self, games_data: dict[int, GameSeriesResponse]) -> None:
        super().__init__(games_data)

    def _detect_halftime(
        self, guest_series: list[tuple[int, Decimal]], host_series: list[tuple[int, Decimal]]
    ) -> tuple[int, int] | None:
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

    def _make_transparent_data_image(self) -> list[tuple[Path, Path]]:
        visuals_paths: list[tuple[Path, Path]] = []

        for game_id, game_data in self._input_data.items():
            guest_series = [(p.timestamp, p.guest_price) for p in game_data.prices if p.guest_price is not None]
            host_series = [(p.timestamp, p.host_price) for p in game_data.prices if p.host_price is not None]

            if not guest_series and not host_series:
                continue

            guest_team = game_data.guest_team
            host_team = game_data.host_team
            guest_score = game_data.guest_score
            host_score = game_data.host_score

            guest_color_scheme = getattr(NBATeamColor, guest_team, None)
            guest_color = guest_color_scheme["guest"] if guest_color_scheme else "#6c757d"
            host_color_scheme = getattr(NBATeamColor, host_team, None)
            host_color = host_color_scheme["host"] if host_color_scheme else "#ced4da"

            game_date = game_data.game_date.isoformat()
            market_type = game_data.market_type

            path_without_bg = self._plot_dir / f"tmp_{game_id}.{self._ext}"
            path_with_bg = self._plot_dir / f"{game_date}_{guest_team}_{host_team}_{game_id}_{market_type}.png"

            if path_with_bg.exists():
                continue

            with plt.rc_context(rc=self._plot_style):  # type: ignore[reportUnknownMemberType]
                plt.figure(figsize=(10, 5))  # type: ignore[reportUnknownMemberType]

                if guest_series:
                    x, y = zip(*guest_series, strict=False)
                    x = [datetime.fromtimestamp(ts) for ts in x]
                    plt.plot(x, y, label=guest_team, color=guest_color, linewidth=5)  # type: ignore[reportUnknownMemberType]

                if host_series:
                    x, y = zip(*host_series, strict=False)
                    x = [datetime.fromtimestamp(ts) for ts in x]
                    plt.plot(x, y, label=host_team, color=host_color, linewidth=5)  # type: ignore[reportUnknownMemberType]

                halftime = self._detect_halftime(guest_series, host_series)
                if halftime:
                    start_ts, end_ts = halftime
                    plt.axvspan(  # type: ignore[reportUnknownMemberType]
                        datetime.fromtimestamp(start_ts),  # type: ignore[arg-type]
                        datetime.fromtimestamp(end_ts),  # type: ignore[arg-type]
                        color="#e9ecef",
                        alpha=0.25,
                        label="HT",
                    )

                plt.title(f"{game_date} • {guest_team} {guest_score}:{host_score} {host_team} • {game_id} {market_type}")  # type: ignore[reportUnknownMemberType]
                plt.xlabel("TIME (UTC)")  # type: ignore[reportUnknownMemberType]
                plt.ylabel("PRICE, USDC")  # type: ignore[reportUnknownMemberType]
                plt.grid(True)  # type: ignore[reportUnknownMemberType]
                plt.legend(facecolor="#6c757d", edgecolor="#6c757d", framealpha=0.5, labelcolor="#e9ecef")  # type: ignore[reportUnknownMemberType]
                plt.tight_layout()
                plt.savefig(path_without_bg, transparent=True)  # type: ignore[reportUnknownMemberType]
                plt.close()

                visuals_paths.append((path_without_bg, path_with_bg))

        return visuals_paths


class OddsFlipChart(Chart):
    _image_bg_bath = settings.BACKGROUND_ODDS_FLIP_PATH

    def __init__(self, games_data: dict[int, GameSeriesResponse]) -> None:
        super().__init__(games_data)

    def _make_transparent_data_image(self) -> list[tuple[Path, Path]]:
        visuals_paths: list[tuple[Path, Path]] = []
        # game_series: dict[int, list[dict[str, Any]]] = {}

        for game_id, game_data in self._input_data.items():

            guest_team = game_data.guest_team
            host_team = game_data.host_team
            guest_score = game_data.guest_score
            host_score = game_data.host_score

            guest_color_scheme = getattr(NBATeamColor, guest_team, None)
            guest_color = guest_color_scheme["guest"] if guest_color_scheme else "#6c757d"
            host_color_scheme = getattr(NBATeamColor, host_team, None)
            host_color = host_color_scheme["host"] if host_color_scheme else "#ced4da"

            game_date = game_data.game_date.isoformat()
            market_type = game_data.market_type

            flip_data = {}
            current_underdog = guest_team
            current_bottom = 1

            for price in game_data.prices:
                price_dif = price.guest_price - price.host_price
                new_underdog = guest_team if price_dif < 0 else host_team

                if new_underdog != current_underdog:
                    flip_data["underdog"] = new_underdog
                    flip_data["underdog_ts"] = price.ts
                    current_underdog = new_underdog

                underdog_price = price.guest_price if current_underdog == guest_team else price.host_price
                new_bottom = underdog_price < current_bottom

                if new_bottom:
                    flip_data["current_bottom"] = underdog_price
                    flip_data["bottom_ts"] = price.ts
                    current_bottom = underdog_price

            guest_series = [(p.timestamp, p.guest_price) for p in game_data.prices if p.guest_price is not None]
            host_series = [(p.timestamp, p.host_price) for p in game_data.prices if p.host_price is not None]

            # price_series = [(p.timestamp, p.guest_price, p.host_price) for p in game_data.prices if p.guest_price is not None and p.host_price is not None]

            path_without_bg = self._chart_dir / f"tmp_{game_id}.png"
            path_with_bg = self._chart_dir / f"{game_date}_{guest_team}_{host_team}_{game_id}_{market_type}.png"

            if path_with_bg.exists():
                logger.debug("File exists: %s", path_with_bg)
                continue

            if not guest_series and not host_series:
                logger.debug("Guest or host series data is absent")
                continue

            with plt.rc_context(rc=self._plot_style):  # type: ignore[reportUnknownMemberType]
                plt.figure(figsize=(10, 5))  # type: ignore[reportUnknownMemberType]

                if guest_series:
                    x, y = zip(*guest_series, strict=False)
                    x = [datetime.fromtimestamp(ts) for ts in x]
                    plt.plot(x, y, label=guest_team, color=guest_color, linewidth=5)  # type: ignore[reportUnknownMemberType]

                if host_series:
                    x, y = zip(*host_series, strict=False)
                    x = [datetime.fromtimestamp(ts) for ts in x]
                    plt.plot(x, y, label=host_team, color=host_color, linewidth=5)  # type: ignore[reportUnknownMemberType]

                plt.title(f"{game_date} • {guest_team} {guest_score}:{host_score} {host_team} • {game_id} {market_type}")  # type: ignore[reportUnknownMemberType]
                plt.xlabel("TIME (UTC)")  # type: ignore[reportUnknownMemberType]
                plt.ylabel("PRICE, USDC")  # type: ignore[reportUnknownMemberType]
                plt.grid(True)  # type: ignore[reportUnknownMemberType]
                plt.legend(facecolor="#f8f9fa", edgecolor="#e9ecef", framealpha=0.15, labelcolor="#e9ecef")  # type: ignore[reportUnknownMemberType]
                plt.tight_layout()
                plt.savefig(path_without_bg, transparent=True)  # type: ignore[reportUnknownMemberType]
                plt.close()

                paths = (path_without_bg, path_with_bg)
                visuals_paths.append(paths)

        return visuals_paths
