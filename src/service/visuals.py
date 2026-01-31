from datetime import datetime
from decimal import Decimal
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from src.config import settings
from src.core.visuals import Chart, Plot, Visuals
from src.service.domain import NBATeamColor
from src.service.schemas import GameSeriesResponse, UnderdogSegment


class GameSeriesVisuals(Visuals):
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

    def _extract_underdog_segments(self, game_data: GameSeriesResponse) -> list[UnderdogSegment]:
        prices = [p for p in game_data.prices if p.guest_price is not None and p.host_price is not None]
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
                        min_price_ts=current_min_ts,
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
                min_price_ts=current_min_ts,
            )
        )

        return segments


class QuoteSeriesPlot(Plot, GameSeriesVisuals):
    _visuals_title = "quote_series"
    _path_img_bg = settings.BACKGROUND_QUOTE_SERIES_PATH
    _img_params = {
        "image_size": (10, 5),
        "image_axis_y_limit": (0.0, 1.0),
        "image_axis_x_label": "DAY, TIME (UTC)",
        "image_axis_y_label": "PRICE, USDC",
        "legend_background_color": "#6c757d",
        "legend_border_color": "#6c757d",
        "legend_transparency": 0.5,
        "legend_labels_color": "#e9ecef",
        "halftime_color": "#e9ecef",
        "halftime_fill_transparency": 0.25,
        "halftime_label": "HALFTIME",
        "halftime_label_axis_y_ancor": 0.1,
        "halftime_label_axis_alignment": "center",
        "halftime_label_font_size": 9,
        "halftime_label_transparency": 1,
        "team_fallback_color_guest": "#6c757d",
        "team_fallback_color_host": "#ced4da",
    }

    def __init__(self, games_data: dict[int, GameSeriesResponse]) -> None:
        super().__init__(games_data)

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
            guest_color = (
                guest_color_scheme["guest"] if guest_color_scheme else self._img_params["team_fallback_color_guest"]
            )
            host_color_scheme = getattr(NBATeamColor, host_team, None)
            host_color = (
                host_color_scheme["host"] if host_color_scheme else self._img_params["team_fallback_color_host"]
            )

            game_date = game_data.game_date.isoformat()
            market_type = game_data.market_type

            path_without_bg = self._plot_dir / f"tmp_{self._visuals_title}_{game_id}.{self._img_ext_transp}"
            path_with_bg = (
                self._plot_dir
                / f"{game_date}_{self._visuals_title}_{guest_team}_{host_team}_{game_id}_{market_type}.{self._img_ext_final}"
            )

            if path_with_bg.exists():
                continue

            with plt.rc_context(rc=self._plot_style):  # type: ignore[reportUnknownMemberType]
                plt.figure(figsize=self._img_params["image_size"])  # type: ignore[reportUnknownMemberType]

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
                        color=self._img_params["halftime_color"],
                        alpha=self._img_params["halftime_fill_transparency"],
                    )

                    mid_ts = (start_ts + end_ts) / 2
                    plt.text(  # type: ignore[reportUnknownMemberType]
                        datetime.fromtimestamp(mid_ts),  # type: ignore[arg-type]
                        self._img_params["halftime_label_axis_y_ancor"],
                        self._img_params["halftime_label"],
                        ha=self._img_params["halftime_label_axis_alignment"],
                        va=self._img_params["halftime_label_axis_alignment"],
                        fontsize=self._img_params["halftime_label_font_size"],
                        color=self._img_params["halftime_color"],
                        alpha=self._img_params["halftime_label_transparency"],
                        clip_on=True,
                    )

                plt.ylim(*self._img_params["image_axis_y_limit"])  # type: ignore[reportUnknownMemberType]
                plt.title(f"{game_date} • {guest_team} {guest_score}:{host_score} {host_team} • {market_type}")  # type: ignore[reportUnknownMemberType]
                plt.xlabel(self._img_params["image_axis_x_label"])  # type: ignore[reportUnknownMemberType]
                plt.ylabel(self._img_params["image_axis_y_label"])  # type: ignore[reportUnknownMemberType]
                plt.grid(True)  # type: ignore[reportUnknownMemberType]
                plt.legend(  # type: ignore[reportUnknownMemberType]
                    facecolor=self._img_params["legend_background_color"],
                    edgecolor=self._img_params["legend_border_color"],
                    framealpha=self._img_params["legend_transparency"],
                    labelcolor=self._img_params["legend_labels_color"],
                )
                plt.tight_layout()
                plt.savefig(path_without_bg, transparent=True)  # type: ignore[reportUnknownMemberType]
                plt.close()

                visuals_paths.append((path_without_bg, path_with_bg))

        return visuals_paths


class OddsFlipChart(Chart, GameSeriesVisuals):
    _visuals_title = "odds_flip"
    _path_img_bg = settings.BACKGROUND_ODDS_FLIP_PATH
    _img_params = {
        "image_size": (10, 5),
        "image_axis_y_limit": (0.0, 0.5),
        "image_axis_x_label": "DAY, TIME (UTC)",
        "image_axis_y_label": "PRICE, USDC",
        "legend_background_color": "#6c757d",
        "legend_border_color": "#6c757d",
        "legend_transparency": 0.5,
        "legend_labels_color": "#e9ecef",
        "underdog_label_color": "#e9ecef",
        "underdog_fill_transparency": 0.12,
        "underdog_fill_border_transparency": 0.3,
        "underdog_fill_border_style": "--",
        "underdog_dot_size": 120,
        "underdog_dot_label_offset": (0, -14),
        "underdog_dot_label_axis_alignment": "center",
        "underdog_dot_label_font_size": 9,
        "underdog_time_label_axis_y_ancor": 0.05,
        "underdog_time_label_axis_alignment": "center",
        "underdog_time_label_font_size": 9,
        "underdog_time_label_transparency": 1.0,
        "team_fallback_color_guest": "#6c757d",
        "team_fallback_color_host": "#ced4da",
    }

    def __init__(self, games_data: dict[int, GameSeriesResponse]) -> None:
        super().__init__(games_data)

    def _make_transparent_data_image(self) -> list[tuple[Path, Path]]:
        visuals_paths: list[tuple[Path, Path]] = []

        for game_id, game_data in self._input_data.items():
            segments = self._extract_underdog_segments(game_data)
            if not segments:
                continue

            guest_team = game_data.guest_team
            host_team = game_data.host_team
            guest_score = game_data.guest_score
            host_score = game_data.host_score
            market_type = game_data.market_type
            game_date = game_data.game_date.isoformat()

            guest_color_scheme = getattr(NBATeamColor, guest_team, None)
            guest_color = (
                guest_color_scheme["guest"] if guest_color_scheme else self._img_params["team_fallback_color_guest"]
            )
            host_color_scheme = getattr(NBATeamColor, host_team, None)
            host_color = (
                host_color_scheme["host"] if host_color_scheme else self._img_params["team_fallback_color_host"]
            )

            path_without_bg = self._chart_dir / f"tmp_{self._visuals_title}_{game_id}.{self._img_ext_transp}"
            path_with_bg = (
                self._chart_dir
                / f"{game_date}_{self._visuals_title}_{guest_team}_{host_team}_{game_id}_{market_type}.{self._img_ext_final}"
            )

            if path_with_bg.exists():
                continue

            start_ts, end_ts = segments[0].start_ts, segments[-1].end_ts

            with plt.rc_context(rc=self._plot_style):  # type: ignore[reportUnknownMemberType]
                plt.figure(figsize=self._img_params["image_size"])  # type: ignore[reportUnknownMemberType]
                legend_items = {}

                for seg in segments:
                    color = guest_color if seg.team == guest_team else host_color
                    label = seg.team if seg.team not in legend_items else None

                    plt.axvspan(  # type: ignore[reportUnknownMemberType]
                        datetime.fromtimestamp(seg.start_ts),  # type: ignore[arg-type]
                        datetime.fromtimestamp(seg.end_ts),  # type: ignore[arg-type]
                        color=color,
                        alpha=self._img_params["underdog_fill_transparency"],
                        zorder=0,
                    )

                    plt.axvline(  # type: ignore[reportUnknownMemberType]
                        datetime.fromtimestamp(seg.start_ts),  # type: ignore[arg-type]
                        color=color,
                        linestyle=self._img_params["underdog_fill_border_style"],
                        alpha=self._img_params["underdog_fill_border_transparency"],
                    )

                    underdog_dot = plt.scatter(  # type: ignore[reportUnknownMemberType]
                        datetime.fromtimestamp(seg.min_price_ts),  # type: ignore[arg-type]
                        float(seg.min_price),
                        color=color,
                        s=self._img_params["underdog_dot_size"],
                        zorder=5,
                        label=label,
                    )

                    plt.annotate(  # type: ignore[reportUnknownMemberType]
                        f"{float(seg.min_price):.3f}",
                        xy=(datetime.fromtimestamp(seg.min_price_ts), float(seg.min_price)),  # type: ignore[arg-type]
                        xytext=self._img_params["underdog_dot_label_offset"],
                        textcoords="offset points",
                        ha=self._img_params["underdog_dot_label_axis_alignment"],
                        va=self._img_params["underdog_dot_label_axis_alignment"],
                        fontsize=self._img_params["underdog_dot_label_font_size"],
                        color=self._img_params["underdog_label_color"],
                    )

                    duration_sec = seg.end_ts - seg.start_ts
                    duration_min = int(duration_sec // 60)

                    mid_ts = (seg.start_ts + seg.end_ts) / 2

                    short_interval = duration_sec < 8 * 60

                    plt.text(  # type: ignore[reportUnknownMemberType]
                        datetime.fromtimestamp(mid_ts),  # type: ignore[arg-type]
                        self._img_params["underdog_time_label_axis_y_ancor"],
                        f"{duration_min} min" if duration_min > 2 else "",
                        ha=self._img_params["underdog_time_label_axis_alignment"],
                        va=self._img_params["underdog_time_label_axis_alignment"],
                        rotation=90 if short_interval else 0,
                        fontsize=self._img_params["underdog_time_label_font_size"],
                        color=self._img_params["underdog_label_color"],
                        alpha=self._img_params["underdog_time_label_transparency"],
                        clip_on=True,
                    )

                    if label:
                        legend_items[label] = underdog_dot

                plt.ylim(*self._img_params["image_axis_y_limit"])  # type: ignore[reportUnknownMemberType]
                plt.xlim(datetime.fromtimestamp(start_ts), datetime.fromtimestamp(end_ts))  # type: ignore[reportUnknownMemberType]
                plt.title(f"{game_date} • {guest_team} {guest_score}:{host_score} {host_team} • Underdog")  # type: ignore[reportUnknownMemberType]
                plt.xlabel(self._img_params["image_axis_x_label"])  # type: ignore[reportUnknownMemberType]
                plt.ylabel(self._img_params["image_axis_y_label"])  # type: ignore[reportUnknownMemberType]
                plt.grid(False)  # type: ignore[reportUnknownMemberType]
                plt.legend(  # type: ignore[reportUnknownMemberType]
                    legend_items.values(),
                    legend_items.keys(),
                    facecolor=self._img_params["legend_background_color"],
                    edgecolor=self._img_params["legend_border_color"],
                    framealpha=self._img_params["legend_transparency"],
                    labelcolor=self._img_params["legend_labels_color"],
                )

                plt.tight_layout()
                plt.savefig(path_without_bg, transparent=True)  # type: ignore[reportUnknownMemberType]
                plt.close()

                visuals_paths.append((path_without_bg, path_with_bg))

        return visuals_paths
