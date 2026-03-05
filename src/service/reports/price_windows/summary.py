from datetime import date, datetime
from pathlib import Path

from src.core.summary import Summary
from src.service.domain import NBATeamSide
from src.service.reports.price_windows.schemas import PriceWindowItem, PriceWindowQuery, WindowSegment
from src.service.reports.utils import is_matching_game


class PriceWindowSummary(Summary):
    _file_output_dir = "price_windows"

    def __init__(self, query: PriceWindowQuery, dataset: dict[int, PriceWindowItem]) -> None:
        super().__init__(query=query, dataset=dataset)

    def _collect_windows(self, games_dict: dict[int, PriceWindowItem], side: NBATeamSide):
        games_with_windows: list[list[WindowSegment]] = []
        all_windows: list[WindowSegment] = []

        for game in games_dict.values():
            windows = game._window_segs.get(side) if game._window_segs else None  # pyright: ignore[reportPrivateUsage]
            if not windows:
                continue
            games_with_windows.append(windows)
            all_windows.extend(windows)

        return games_with_windows, all_windows

    def _compute_stats_text(
        self, games_dict: dict[int, PriceWindowItem], team: str | None = None, team_vs: str | None = None
    ) -> str:
        total_games = len(games_dict)
        scope = team if team else "ALL"
        if total_games == 0:
            return f"{scope}: no games.\n"

        output: list[str] = []
        for side in NBATeamSide:
            games, windows = self._collect_windows(games_dict, side)

            games_with_window = len(games)
            window_count = len(windows)
            rate = games_with_window / total_games if total_games else 0

            if games_with_window == 0:
                avg_windows = repeat_rate = avg_duration = median_duration = 0
            else:
                durations = [(w.end_ts - w.start_ts) / 60 for w in windows]
                avg_windows = window_count / games_with_window
                repeat_rate = sum(len(g) >= 2 for g in games) / games_with_window
                avg_duration = sum(durations) / window_count if window_count else 0
                median_duration = sorted(durations)[window_count // 2] if window_count else 0

            output.append(
                f"# {scope} {side.upper()}{' vs ' + team_vs if team_vs else ''}:\n"
                f"    Games: {games_with_window}/{total_games} ({rate:.2%})\n"
                f"    Windows: {window_count} ({avg_windows:.2f}/game)\n"
                f"    Repeat entry (>=2): {repeat_rate:.2%}\n"
                f"    Duration AVG: {avg_duration:.1f} min\n"
                f"    Duration MED: {median_duration:.1f} min"
            )
        output.append("")
        return "\n".join(output)

    def _make_data_summary(self) -> Path:
        team = self._query.team.name
        team_vs = self._query.team_vs.name if self._query.team_vs else None
        window_start = self._query.window_start
        window_end = self._query.window_end

        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_dir = self._path_shared_dir / self._file_output_dir
        report_path = report_dir / f"{now}_{team}_{window_start}-{window_end}.{self._report_ext}"

        all_games: dict[int, PriceWindowItem] = self._dataset
        team_games = {id: game for id, game in all_games.items() if is_matching_game(game, team)}
        team_vs_games = {id: game for id, game in all_games.items() if is_matching_game(game, team, team_vs)}

        report_blocks = [
            f"Window: {window_start} -> {window_end}",
            f"Date: {date.today()}\n",
            self._compute_stats_text(all_games),
        ]

        if team_games:
            report_blocks.append(self._compute_stats_text(team_games, team))

        if team_vs_games:
            report_blocks.append(self._compute_stats_text(team_vs_games, team, team_vs))

        self._report_text = "\n".join(report_blocks)
        return report_path
