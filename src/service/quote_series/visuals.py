from datetime import datetime, timedelta
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt

from src.config import settings
from src.core.visuals import Plot
from src.service.domain import NBATeamColor, NBATeamSide
from src.service.quote_series.schemas import QuoteSeriesItem, QuoteSeriesQuery


class QuoteSeriesPlot(Plot):
    _img_output_dir = "quote_series"
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
        "underdog_dot_border_color": "#e9ecef",
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

    def __init__(self, query: QuoteSeriesQuery, dataset: dict[int, QuoteSeriesItem]) -> None:
        super().__init__(query=query, dataset=dataset)

    def _make_transparent_data_image(self) -> list[tuple[Path | None, Path]]:
        visuals_paths: list[tuple[Path | None, Path]] = []

        for game_id, game_data in self._dataset.items():
            guest_series = [(p.timestamp, p.guest_price) for p in game_data.price_series if p.guest_price is not None]
            host_series = [(p.timestamp, p.host_price) for p in game_data.price_series if p.host_price is not None]

            if not guest_series and not host_series:
                continue

            guest_team = game_data.guest_team
            host_team = game_data.host_team
            guest_score = game_data.guest_score
            host_score = game_data.host_score

            guest_color_scheme = getattr(NBATeamColor, guest_team, None)
            guest_color = (
                guest_color_scheme[NBATeamSide.GUEST]
                if guest_color_scheme
                else self._img_params["team_fallback_color_guest"]
            )
            host_color_scheme = getattr(NBATeamColor, host_team, None)
            host_color = (
                host_color_scheme[NBATeamSide.HOST]
                if host_color_scheme
                else self._img_params["team_fallback_color_host"]
            )

            game_date = game_data.game_date.isoformat()
            market_type = game_data.market_type

            halftime_segment = game_data.halftime_seg
            underdog_segments = game_data.underdog_segs

            path_without_bg = self._plot_dir / f"tmp_{game_id}.{self._img_ext_transp}"
            path_with_bg = (
                self._plot_dir / f"{game_date}_{guest_team}_{host_team}_{game_id}_{market_type}.{self._img_ext_final}"
            )

            if path_with_bg.exists():
                visuals_paths.append((None, path_with_bg))
                continue

            if not underdog_segments:
                continue

            match_start_ts = underdog_segments[0].start_ts
            match_end_ts = underdog_segments[-1].end_ts

            with plt.rc_context(rc=self._plot_style):  # pyright: ignore[reportUnknownMemberType]
                plt.figure(figsize=self._img_params["image_size"])  # pyright: ignore[reportUnknownMemberType]

                if guest_series:
                    x, y = zip(*guest_series, strict=False)
                    x_rel = [datetime(1900, 1, 1) + timedelta(seconds=ts - match_start_ts) for ts in x]
                    plt.plot(  # pyright: ignore[reportUnknownMemberType]
                        x_rel,  # pyright: ignore[reportArgumentType]
                        y,
                        label=guest_team,
                        color=guest_color,
                        linewidth=self._img_params["team_probability_line_width"],
                    )

                if host_series:
                    x, y = zip(*host_series, strict=False)
                    x_rel = [datetime(1900, 1, 1) + timedelta(seconds=ts - match_start_ts) for ts in x]
                    plt.plot(  # pyright: ignore[reportUnknownMemberType]
                        x_rel,  # pyright: ignore[reportArgumentType]
                        y,
                        label=host_team,
                        color=host_color,
                        linewidth=self._img_params["team_probability_line_width"],
                    )

                if halftime_segment:
                    plt.axvspan(  # pyright: ignore[reportUnknownMemberType]
                        datetime(1900, 1, 1)
                        + timedelta(
                            seconds=halftime_segment.start_ts - match_start_ts
                        ),  # pyright: ignore[reportArgumentType]
                        datetime(1900, 1, 1)
                        + timedelta(
                            seconds=halftime_segment.end_ts - match_start_ts
                        ),  # pyright: ignore[reportArgumentType]
                        color=self._img_params["halftime_color"],
                        alpha=self._img_params["halftime_fill_transparency"],
                    )
                    mid_ht = datetime(1900, 1, 1) + timedelta(
                        seconds=(halftime_segment.start_ts + halftime_segment.end_ts) / 2 - match_start_ts
                    )
                    plt.text(  # pyright: ignore[reportUnknownMemberType]
                        mid_ht,  # pyright: ignore[reportArgumentType]
                        self._img_params["halftime_label_axis_y_ancor"],
                        self._img_params["halftime_label"],
                        ha=self._img_params["halftime_label_axis_alignment"],
                        va=self._img_params["halftime_label_axis_alignment"],
                        fontsize=self._img_params["halftime_label_font_size"],
                        color=self._img_params["halftime_color"],
                        alpha=self._img_params["halftime_label_transparency"],
                        clip_on=True,
                        zorder=5,
                    )

                for u_seg in underdog_segments:
                    u_seg_start = datetime(1900, 1, 1) + timedelta(seconds=u_seg.start_ts - match_start_ts)
                    u_seg_end = datetime(1900, 1, 1) + timedelta(seconds=u_seg.end_ts - match_start_ts)
                    u_seg_mid = datetime(1900, 1, 1) + timedelta(
                        seconds=(u_seg.start_ts + u_seg.end_ts) / 2 - match_start_ts
                    )
                    u_seg_duration_min = int((u_seg.end_ts - u_seg.start_ts) // 60)

                    underdog_color = guest_color if u_seg.team == guest_team else host_color

                    plt.axvspan(  # pyright: ignore[reportUnknownMemberType]
                        u_seg_start,  # pyright: ignore[reportArgumentType]
                        u_seg_end,  # pyright: ignore[reportArgumentType]
                        color=underdog_color,
                        alpha=self._img_params["underdog_fill_transparency"],
                        zorder=0,
                    )
                    plt.axvline(  # pyright: ignore[reportUnknownMemberType]
                        u_seg_start,  # pyright: ignore[reportArgumentType]
                        color=underdog_color,
                        linestyle=self._img_params["underdog_fill_border_style"],
                        alpha=self._img_params["underdog_fill_border_transparency"],
                    )

                    plt.scatter(  # pyright: ignore[reportUnknownMemberType]
                        datetime(1900, 1, 1)
                        + timedelta(seconds=u_seg.min_ts - match_start_ts),  # pyright: ignore[reportArgumentType]
                        float(u_seg.min_price),
                        color=underdog_color,
                        edgecolor=self._img_params["underdog_dot_border_color"],
                        linewidths=self._img_params["underdog_dot_sborder_width"],
                        s=self._img_params["underdog_dot_size"],
                        zorder=5,
                        clip_on=False,
                    )

                    plt.annotate(  # pyright: ignore[reportUnknownMemberType]
                        f"{float(u_seg.min_price):.3f}",
                        xy=(
                            datetime(1900, 1, 1)
                            + timedelta(seconds=u_seg.min_ts - match_start_ts),  # pyright: ignore[reportArgumentType]
                            float(u_seg.min_price),
                        ),
                        xytext=self._img_params["underdog_dot_label_offset"],
                        textcoords="offset points",
                        ha=self._img_params["underdog_dot_label_axis_alignment"],
                        va=self._img_params["underdog_dot_label_axis_alignment"],
                        fontsize=self._img_params["underdog_dot_label_font_size"],
                        color=self._img_params["underdog_label_color"],
                    )

                    plt.text(  # pyright: ignore[reportUnknownMemberType]
                        u_seg_mid,  # pyright: ignore[reportArgumentType]
                        self._img_params["underdog_time_label_axis_y_ancor"],
                        f"{u_seg_duration_min} min" if u_seg_duration_min > 2 else "",
                        ha=self._img_params["underdog_time_label_axis_alignment"],
                        va=self._img_params["underdog_time_label_axis_alignment"],
                        rotation=90 if (u_seg.end_ts - u_seg.start_ts) < 8 * 60 else 0,
                        fontsize=self._img_params["underdog_time_label_font_size"],
                        color=self._img_params["underdog_label_color"],
                        alpha=self._img_params["underdog_time_label_transparency"],
                        clip_on=True,
                    )

                plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))

                plt.ylim(*self._img_params["image_axis_y_limit"])  # pyright: ignore[reportUnknownMemberType]
                plt.xlim(  # pyright: ignore[reportUnknownMemberType]
                    datetime(1900, 1, 1), datetime(1900, 1, 1) + timedelta(seconds=match_end_ts - match_start_ts)
                )

                plt.title(  # pyright: ignore[reportUnknownMemberType]
                    f"{game_date} • {guest_team} {guest_score}:{host_score} {host_team} • {market_type} {game_id}"
                )
                plt.xlabel(self._img_params["image_axis_x_label"])  # pyright: ignore[reportUnknownMemberType]
                plt.ylabel(self._img_params["image_axis_y_label"])  # pyright: ignore[reportUnknownMemberType]
                plt.grid(True)  # pyright: ignore[reportUnknownMemberType]
                plt.legend(  # pyright: ignore[reportUnknownMemberType]
                    facecolor=self._img_params["legend_background_color"],
                    edgecolor=self._img_params["legend_border_color"],
                    framealpha=self._img_params["legend_transparency"],
                    labelcolor=self._img_params["legend_labels_color"],
                )
                plt.tight_layout()
                plt.savefig(path_without_bg, transparent=True)  # pyright: ignore[reportUnknownMemberType]
                plt.close()

                visuals_paths.append((path_without_bg, path_with_bg))

        return visuals_paths
