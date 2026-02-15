from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.container import BarContainer
from numpy.typing import NDArray

from src.config import settings
from src.core.visuals import Chart, Plot
from src.service.domain import NBATeamColor, NBATeamSide
from src.service.schemas import PriceWindowItem, QuoteSeriesItem, ReportQuery


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

    def __init__(self, query: ReportQuery, dataset: dict[int, QuoteSeriesItem]) -> None:
        super().__init__(query=query, dataset=dataset)

    def _make_transparent_data_image(self) -> list[tuple[Path, Path]]:
        visuals_paths: list[tuple[Path, Path]] = []

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
                    plt.axvspan(  # type: ignore[reportUnknownMemberType]
                        datetime(1900, 1, 1) + timedelta(seconds=halftime_segment.start_ts - match_start_ts),  # type: ignore[arg-type]
                        datetime(1900, 1, 1) + timedelta(seconds=halftime_segment.end_ts - match_start_ts),  # type: ignore[arg-type]
                        color=self._img_params["halftime_color"],
                        alpha=self._img_params["halftime_fill_transparency"],
                    )
                    mid_ht = datetime(1900, 1, 1) + timedelta(
                        seconds=(halftime_segment.start_ts + halftime_segment.end_ts) / 2 - match_start_ts
                    )
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

                    plt.axvspan(u_seg_start, u_seg_end, color=underdog_color, alpha=self._img_params["underdog_fill_transparency"], zorder=0)  # type: ignore[reportUnknownMemberType]
                    plt.axvline(  # type: ignore[reportUnknownMemberType]
                        u_seg_start,  # type: ignore[arg-type]
                        color=underdog_color,
                        linestyle=self._img_params["underdog_fill_border_style"],
                        alpha=self._img_params["underdog_fill_border_transparency"],
                    )

                    plt.scatter(  # type: ignore[reportUnknownMemberType]
                        datetime(1900, 1, 1) + timedelta(seconds=u_seg.min_ts - match_start_ts),  # type: ignore[arg-type]
                        float(u_seg.min_price),
                        color=underdog_color,
                        edgecolor=self._img_params["underdog_dot_border_color"],
                        linewidths=self._img_params["underdog_dot_sborder_width"],
                        s=self._img_params["underdog_dot_size"],
                        zorder=5,
                        clip_on=False,
                    )

                    plt.annotate(  # type: ignore[reportUnknownMemberType]
                        f"{float(u_seg.min_price):.3f}",
                        xy=(datetime(1900, 1, 1) + timedelta(seconds=u_seg.min_ts - match_start_ts), float(u_seg.min_price)),  # type: ignore[arg-type]
                        xytext=self._img_params["underdog_dot_label_offset"],
                        textcoords="offset points",
                        ha=self._img_params["underdog_dot_label_axis_alignment"],
                        va=self._img_params["underdog_dot_label_axis_alignment"],
                        fontsize=self._img_params["underdog_dot_label_font_size"],
                        color=self._img_params["underdog_label_color"],
                    )

                    plt.text(  # type: ignore[reportUnknownMemberType]
                        u_seg_mid,  # type: ignore[arg-type]
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

                plt.ylim(*self._img_params["image_axis_y_limit"])  # type: ignore[reportUnknownMemberType]
                plt.xlim(datetime(1900, 1, 1), datetime(1900, 1, 1) + timedelta(seconds=match_end_ts - match_start_ts))  # type: ignore[reportUnknownMemberType]

                plt.title(f"{game_date} • {guest_team} {guest_score}:{host_score} {host_team} • {market_type} {game_id}")  # type: ignore[reportUnknownMemberType]
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


class PriceWindowChart(Chart):
    _img_output_dir = "price_windows"
    _path_img_bg = settings.BACKGROUND_PRICE_WINDOW_PATH
    _logo_dir = settings.TEAM_LOGO_DIR
    _img_params = {
        "image_size": (10, 5),
        "bar_width": 0.40,
        "bar_transparency": 0.7,
        "bar_label_color": "#e9ecef",
        "bar_label_fontweight": "bold",
        "bar_label_axis_hor_alignment": "center",
        "bar_label_axis_ver_alignment": "bottom",
        "bar_label_size_percentage": 17,
        "bar_label_size_game_count": 13,
        "axis_y_limit": (0.0, 100.0),
        "axis_y_label": "% OF GAMES",
        "axis_y_grid_style": "--",
        "axis_y_grid_transparency": 0.25,
        "team_fallback_color_guest": "#6c757d",
        "team_fallback_color_host": "#ced4da",
        "legend_background_color": "#6c757d",
        "legend_border_color": "#6c757d",
        "legend_transparency": 0.5,
        "legend_labels_color": "#e9ecef",
    }

    def __init__(self, query: ReportQuery, dataset: dict[int, QuoteSeriesItem]) -> None:
        super().__init__(query=query, dataset=dataset)

    def _compute_counts(self, games_dict: dict[int, PriceWindowItem]):
        counts = {NBATeamSide.GUEST: {"games": 0, "windows": 0}, NBATeamSide.HOST: {"games": 0, "windows": 0}}
        for side in [NBATeamSide.GUEST, NBATeamSide.HOST]:
            games_with_windows: list[Any] = []
            all_windows: list[Any] = []
            for game in games_dict.values():
                windows = getattr(game, "_window_segs", {}).get(side)
                if windows:
                    games_with_windows.append(windows)
                    all_windows.extend(windows)
            counts[side]["games"] = len(games_with_windows)
            counts[side]["windows"] = len(all_windows)
        return counts

    def _draw_bar_group(
        self,
        ax: Axes,
        positions: NDArray[np.float64] | list[float],
        values: list[float],
        totals: list[tuple[int, int]],
        width: float,
        color: str,
        label: str,
    ) -> BarContainer:
        min_height = 0.5
        heights = [v if v > 0 else min_height for v in values]

        bars = ax.bar(  # type: ignore[reportUnknownMemberType]
            x=positions,
            height=heights,
            width=width,
            label=label,
            color=color,
            alpha=self._img_params["bar_transparency"],
        )

        for bar, val, (matched, total) in zip(bars, values, totals, strict=False):  # type: ignore[reportUnknownMemberType]
            pos_hor = bar.get_x() + bar.get_width() / 2  # type: ignore[reportUnknownMemberType]
            pos_ver = bar.get_height() + 1  # type: ignore[reportUnknownMemberType]

            if val == 0:
                bar.set_alpha(0)  # type: ignore[reportUnknownMemberType]
                ax.text(  # type: ignore[reportUnknownMemberType]
                    x=pos_hor,  # type: ignore[reportUnknownMemberType]
                    y=pos_ver,  # type: ignore[reportUnknownMemberType]
                    s="NO CASES",
                    ha=self._img_params["bar_label_axis_hor_alignment"],
                    va=self._img_params["bar_label_axis_ver_alignment"],
                    fontsize=self._img_params["bar_label_size_game_count"],
                    fontweight=self._img_params["bar_label_fontweight"],
                    color=color,
                )
            else:
                ax.text(  # type: ignore[reportUnknownMemberType]
                    x=pos_hor,  # type: ignore[reportUnknownMemberType]
                    y=pos_ver,  # type: ignore[reportUnknownMemberType]
                    s=f"{val:.1f}%",
                    ha=self._img_params["bar_label_axis_hor_alignment"],
                    va=self._img_params["bar_label_axis_ver_alignment"],
                    fontsize=self._img_params["bar_label_size_percentage"],
                    fontweight=self._img_params["bar_label_fontweight"],
                    color=self._img_params["bar_label_color"],
                )

                ax.text(  # type: ignore[reportUnknownMemberType]
                    x=pos_hor,  # type: ignore[reportUnknownMemberType]
                    y=2,
                    s=f"{matched} / {total}",
                    ha=self._img_params["bar_label_axis_hor_alignment"],
                    va=self._img_params["bar_label_axis_ver_alignment"],
                    fontsize=self._img_params["bar_label_size_game_count"],
                    fontweight=self._img_params["bar_label_fontweight"],
                    color=self._img_params["bar_label_color"],
                )

        return bars

    def _make_transparent_data_image(self) -> list[tuple[Path, Path]]:
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        all_teams = "ALL TEAMS"
        team = self._query.team.name
        team_vs = self._query.team_vs.name if self._query.team_vs else all_teams
        window_start = self._query.start_price
        window_end = self._query.end_price

        color_scheme = getattr(NBATeamColor, team, None)
        guest_color = color_scheme[NBATeamSide.GUEST] if color_scheme else self._img_params["team_fallback_color_guest"]
        host_color = color_scheme[NBATeamSide.HOST] if color_scheme else self._img_params["team_fallback_color_host"]

        report_dir = self._chart_dir
        report_dir.mkdir(parents=True, exist_ok=True)

        path_without_bg = report_dir / f"tmp_{now}_{team}_{window_start}-{window_end}.{self._img_ext_transp}"
        path_with_bg = report_dir / f"{now}_{team}_{window_start}-{window_end}.{self._img_ext_final}"

        all_games: dict[int, PriceWindowItem] = self._dataset
        team_games = {id: g for id, g in all_games.items() if g.guest_team == team or g.host_team == team}
        team_vs_games = {
            id: g
            for id, g in all_games.items()
            if (g.guest_team == team and g.host_team == team_vs) or (g.host_team == team and g.guest_team == team_vs)
        }

        counts_all = self._compute_counts(all_games)
        counts_team = self._compute_counts(team_games)
        counts_vs = self._compute_counts(team_vs_games)

        categories = [
            (counts_all[NBATeamSide.GUEST]["games"], len(all_games)),
            (counts_all[NBATeamSide.HOST]["games"], len(all_games)),
            (counts_team[NBATeamSide.GUEST]["games"], len(team_games)),
            (counts_team[NBATeamSide.HOST]["games"], len(team_games)),
            (counts_vs[NBATeamSide.GUEST]["games"], len(team_vs_games)),
            (counts_vs[NBATeamSide.HOST]["games"], len(team_vs_games)),
        ]

        totals_data = [
            (counts_all[NBATeamSide.GUEST]["games"], len(all_games)),
            (counts_all[NBATeamSide.HOST]["games"], len(all_games)),
            (counts_team[NBATeamSide.GUEST]["games"], len(team_games)),
            (counts_team[NBATeamSide.HOST]["games"], len(team_games)),
            (counts_vs[NBATeamSide.GUEST]["games"], len(team_vs_games)),
            (counts_vs[NBATeamSide.HOST]["games"], len(team_vs_games)),
        ]

        values = [games / max(1, total) * 100 for games, total in categories]
        values = [
            values[0],
            values[1],  # ALL
            values[2],
            values[3],  # TEAM
            values[4],
            values[5],  # VS TEAM
        ]

        with plt.rc_context(self._plot_style):  # type: ignore[reportUnknownMemberType]
            fig, ax = plt.subplots(figsize=self._img_params["image_size"], facecolor="none")  # type: ignore[reportUnknownMemberType]

            guest_vals = [values[0], values[2], values[4]] if team_vs != all_teams else [values[0], values[2]]
            host_vals = [values[1], values[3], values[5]] if team_vs != all_teams else [values[1], values[3]]
            guest_totals = (
                [totals_data[0], totals_data[2], totals_data[4]]
                if team_vs != all_teams
                else [totals_data[0], totals_data[2]]
            )
            host_totals = (
                [totals_data[1], totals_data[3], totals_data[5]]
                if team_vs != all_teams
                else [totals_data[1], totals_data[3]]
            )
            tick_labels = (
                [all_teams, f"{team} vs {all_teams}", f"{team} vs {team_vs}"]
                if team_vs != all_teams
                else [all_teams, f"{team} vs {all_teams}"]
            )
            bar_spacing = np.arange(3 if team_vs != all_teams else 2)

            self._draw_bar_group(
                ax=ax,
                positions=bar_spacing - self._img_params["bar_width"] / 2,
                values=guest_vals,
                totals=guest_totals,
                width=self._img_params["bar_width"],
                color=guest_color,
                label=NBATeamSide.GUEST.upper(),
            )

            self._draw_bar_group(
                ax=ax,
                positions=bar_spacing + self._img_params["bar_width"] / 2,
                values=host_vals,
                totals=host_totals,
                width=self._img_params["bar_width"],
                color=host_color,
                label=NBATeamSide.HOST.upper(),
            )

            ax.set_xticks(bar_spacing)  # type: ignore[reportUnknownMemberType]
            ax.set_xticklabels(tick_labels)  # type: ignore[reportUnknownMemberType]

            max_val = max(guest_vals + host_vals)
            upper_limit = max_val * 1.15 if max_val > 0 else 10
            ax.set_ylim(0, upper_limit)

            ax.set_ylabel(self._img_params["axis_y_label"])  # type: ignore[reportUnknownMemberType]
            plt.title(f"{date.today()} • {window_start}-{window_end} Window Stats • {team} vs {team_vs}")  # type: ignore[reportUnknownMemberType]

            ax.grid(axis="x", visible=False)  # type: ignore[reportUnknownMemberType]
            ax.grid(  # type: ignore[reportUnknownMemberType]
                axis="y",
                linestyle=self._img_params["axis_y_grid_style"],
                alpha=self._img_params["axis_y_grid_transparency"],
            )

            plt.legend(  # type: ignore[reportUnknownMemberType]
                facecolor=self._img_params["legend_background_color"],
                edgecolor=self._img_params["legend_border_color"],
                framealpha=self._img_params["legend_transparency"],
                labelcolor=self._img_params["legend_labels_color"],
            )

            plt.tight_layout()
            plt.savefig(path_without_bg, transparent=True)  # type: ignore[reportUnknownMemberType]
            plt.close(fig)

        return [(path_without_bg, path_with_bg)]
