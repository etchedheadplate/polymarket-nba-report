from typing import Any

from src.database.connection import sync_session_maker
from src.service.domain import GAME_STATUS_MAP, GameStatus
from src.service.repos import NBAGamesRepo
from src.service.schemas import EventsFutureQuery, EventsPastQuery


def get_game_events(query: EventsPastQuery | EventsFutureQuery) -> dict[str, Any]:
    with sync_session_maker() as session:
        rows = NBAGamesRepo().get_game_events(
            session=session,
            query=query,
        )

    schedule: dict[str, Any] = {}
    for id, date, g_team, h_team, g_score, h_score, status in rows:
        schedule[id] = {
            "game_date": date,
            "guest_team": g_team,
            "host_team": h_team,
            "guest_score": g_score,
            "host_score": h_score,
            "game_status": GAME_STATUS_MAP[GameStatus(status)],
        }

    return schedule


_event_map: dict[str, type[EventsPastQuery] | type[EventsFutureQuery]] = {
    "past": EventsPastQuery,
    "future": EventsFutureQuery,
}


def create_events_query(payload: dict[str, Any]) -> EventsPastQuery | EventsFutureQuery:
    event_cls = _event_map[payload["period"]]
    query = payload["query"]

    return event_cls(
        start_date=query["start_date"],
        end_date=query["end_date"],
        team=query["team"],
        team_vs=query["team_vs"],
        team_side=query["team_side"],
    )


if __name__ == "__main__":
    from datetime import date, timedelta

    from src.service.domain import NBATeam

    today = date.today()
    last_year = today - timedelta(weeks=52)
    last_week = today - timedelta(weeks=1)
    next_week = today + timedelta(weeks=1)

    past_query = EventsPastQuery(start_date=last_year, end_date=today, team=NBATeam.BOS)

    future_query = EventsFutureQuery(start_date=last_week, end_date=today, team=None)

    schedule = get_game_events(past_query)
    for id, game in schedule.items():
        print(id, game)
