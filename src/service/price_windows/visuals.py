from datetime import date, datetime
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.container import BarContainer
from numpy.typing import NDArray

from src.config import settings
from src.core.visuals import Chart
from src.service.domain import NBATeamColor, NBATeamSide
from src.service.price_windows.schemas import PriceWindowItem, PriceWindowQuery


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

    def __init__(self, query: PriceWindowQuery, dataset: dict[int, PriceWindowItem]) -> None:
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
        window_start = self._query.window_start
        window_end = self._query.window_end

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
