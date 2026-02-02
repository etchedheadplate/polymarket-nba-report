from datetime import datetime, timedelta
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt

from src.config import settings
from src.core.visuals import Plot
from src.service.domain import NBATeamColor
from src.service.schemas import GameSeriesResponse


class QuoteSeriesPlot(Plot):
    _visuals_title = "quote_series"
    _path_img_bg = settings.BACKGROUND_QUOTE_SERIES_PATH
    _img_params = {
        "image_size": (10, 5),
        "image_axis_y_limit": (0.0, 1.0),
        "image_axis_x_label": "GAME DURATION",
        "image_axis_y_label": "WIN PROBABILITY",
        "team_fallback_color_guest": "#6c757d",
        "team_fallback_color_host": "#ced4da",
        "team_probability_line_width": 5,
        "legend_background_color": "#6c757d",
        "legend_border_color": "#6c757d",
        "legend_transparency": 0.5,
        "legend_labels_color": "#e9ecef",
        "halftime_color": "#e9ecef",
        "halftime_fill_transparency": 0.25,
        "halftime_label": "HALFTIME",
        "halftime_label_axis_y_ancor": 0.95,
        "halftime_label_axis_alignment": "center",
        "halftime_label_font_size": 9,
        "halftime_label_transparency": 1,
        "underdog_label_color": "#e9ecef",
        "underdog_fill_transparency": 0.125,
        "underdog_fill_border_transparency": 0.25,
        "underdog_fill_border_style": "--",
        "underdog_dot_border_color": "#e9ecef",  # цвет обводки
        "underdog_dot_sborder_width": 1,
        "underdog_dot_size": 75,
        "underdog_dot_label_offset": (0, -15),
        "underdog_dot_label_axis_alignment": "center",
        "underdog_dot_label_font_size": 9,
        "underdog_time_label_axis_y_ancor": 0.075,
        "underdog_time_label_axis_alignment": "center",
        "underdog_time_label_font_size": 9,
        "underdog_time_label_transparency": 1.0,
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

            halftime_segment = game_data.halftime_ts
            underdog_segments = game_data.underdog_segs

            path_without_bg = self._plot_dir / f"tmp_{self._visuals_title}_{game_id}.{self._img_ext_transp}"
            path_with_bg = (
                self._plot_dir
                / f"{game_date}_{self._visuals_title}_{guest_team}_{host_team}_{game_id}_{market_type}.{self._img_ext_final}"
            )

            if path_with_bg.exists():
                continue

            if not underdog_segments:
                continue

            match_start_ts = underdog_segments[0].start_ts
            match_end_ts = underdog_segments[-1].end_ts

            with plt.rc_context(rc=self._plot_style):  # type: ignore[reportUnknownMemberType]
                plt.figure(figsize=self._img_params["image_size"])  # type: ignore[reportUnknownMemberType]

                if guest_series:
                    x, y = zip(*guest_series, strict=False)
                    x_rel = [datetime(1900, 1, 1) + timedelta(seconds=ts - match_start_ts) for ts in x]
                    plt.plot(x_rel, y, label=guest_team, color=guest_color, linewidth=self._img_params["team_probability_line_width"])  # type: ignore[reportUnknownMemberType]

                if host_series:
                    x, y = zip(*host_series, strict=False)
                    x_rel = [datetime(1900, 1, 1) + timedelta(seconds=ts - match_start_ts) for ts in x]
                    plt.plot(x_rel, y, label=host_team, color=host_color, linewidth=self._img_params["team_probability_line_width"])  # type: ignore[reportUnknownMemberType]

                if halftime_segment:
                    ht_start_ts, ht_end_ts = halftime_segment
                    plt.axvspan(  # type: ignore[reportUnknownMemberType]
                        datetime(1900, 1, 1) + timedelta(seconds=ht_start_ts - match_start_ts),  # type: ignore[arg-type]
                        datetime(1900, 1, 1) + timedelta(seconds=ht_end_ts - match_start_ts),  # type: ignore[arg-type]
                        color=self._img_params["halftime_color"],
                        alpha=self._img_params["halftime_fill_transparency"],
                    )
                    mid_ht = datetime(1900, 1, 1) + timedelta(seconds=(ht_start_ts + ht_end_ts) / 2 - match_start_ts)
                    plt.text(  # type: ignore[reportUnknownMemberType]
                        mid_ht,  # type: ignore[arg-type]
                        self._img_params["halftime_label_axis_y_ancor"],
                        self._img_params["halftime_label"],
                        ha=self._img_params["halftime_label_axis_alignment"],
                        va=self._img_params["halftime_label_axis_alignment"],
                        fontsize=self._img_params["halftime_label_font_size"],
                        color=self._img_params["halftime_color"],
                        alpha=self._img_params["halftime_label_transparency"],
                        clip_on=True,
                    )

                for seg in underdog_segments:
                    seg_start = datetime(1900, 1, 1) + timedelta(seconds=seg.start_ts - match_start_ts)
                    seg_end = datetime(1900, 1, 1) + timedelta(seconds=seg.end_ts - match_start_ts)
                    seg_mid = datetime(1900, 1, 1) + timedelta(seconds=(seg.start_ts + seg.end_ts) / 2 - match_start_ts)

                    underdog_color = guest_color if seg.team == guest_team else host_color

                    plt.axvspan(seg_start, seg_end, color=underdog_color, alpha=self._img_params["underdog_fill_transparency"], zorder=0)  # type: ignore[reportUnknownMemberType]
                    plt.axvline(  # type: ignore[reportUnknownMemberType]
                        seg_start,  # type: ignore[arg-type]
                        color=underdog_color,
                        linestyle=self._img_params["underdog_fill_border_style"],
                        alpha=self._img_params["underdog_fill_border_transparency"],
                    )

                    plt.scatter(  # type: ignore[reportUnknownMemberType]
                        datetime(1900, 1, 1) + timedelta(seconds=seg.min_price_ts - match_start_ts),  # type: ignore[arg-type]
                        float(seg.min_price),
                        color=underdog_color,
                        edgecolor=self._img_params["underdog_dot_border_color"],
                        linewidths=self._img_params["underdog_dot_sborder_width"],
                        s=self._img_params["underdog_dot_size"],
                        zorder=5,
                    )

                    plt.annotate(  # type: ignore[reportUnknownMemberType]
                        f"{float(seg.min_price):.3f}",
                        xy=(datetime(1900, 1, 1) + timedelta(seconds=seg.min_price_ts - match_start_ts), float(seg.min_price)),  # type: ignore[arg-type]
                        xytext=self._img_params["underdog_dot_label_offset"],
                        textcoords="offset points",
                        ha=self._img_params["underdog_dot_label_axis_alignment"],
                        va=self._img_params["underdog_dot_label_axis_alignment"],
                        fontsize=self._img_params["underdog_dot_label_font_size"],
                        color=self._img_params["underdog_label_color"],
                    )

                    seg_duration_min = int((seg.end_ts - seg.start_ts) // 60)
                    plt.text(  # type: ignore[reportUnknownMemberType]
                        seg_mid,  # type: ignore[arg-type]
                        self._img_params["underdog_time_label_axis_y_ancor"],
                        f"{seg_duration_min} min" if seg_duration_min > 2 else "",
                        ha=self._img_params["underdog_time_label_axis_alignment"],
                        va=self._img_params["underdog_time_label_axis_alignment"],
                        rotation=90 if (seg.end_ts - seg.start_ts) < 8 * 60 else 0,
                        fontsize=self._img_params["underdog_time_label_font_size"],
                        color=self._img_params["underdog_label_color"],
                        alpha=self._img_params["underdog_time_label_transparency"],
                        clip_on=True,
                    )

                plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))

                plt.ylim(*self._img_params["image_axis_y_limit"])  # type: ignore[reportUnknownMemberType]
                plt.xlim(datetime(1900, 1, 1), datetime(1900, 1, 1) + timedelta(seconds=match_end_ts - match_start_ts))  # type: ignore[reportUnknownMemberType]

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
