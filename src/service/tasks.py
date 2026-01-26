from decimal import Decimal

from src.database.connection import async_session_maker
from src.service.domain import MarketType, NBATeam
from src.service.repos import NBAGamesRepo


async def get_team_games(team: NBATeam) -> list[int]:
    async with async_session_maker() as session:
        games = await NBAGamesRepo().get_past_team_games_ids(session, team)
    return games


async def get_teams_matchups(guest_team: NBATeam, host_team: NBATeam) -> list[int]:
    async with async_session_maker() as session:
        matchups = await NBAGamesRepo().get_past_teams_matchups_ids(session, guest_team, host_team)
    return matchups


async def get_teams_matchups_data(
    guest_team: NBATeam, host_team: NBATeam, market_type: MarketType = MarketType.moneyline
) -> dict[str, dict[str, dict[int, dict[str, Decimal]]]]:
    async with async_session_maker() as session:
        raw_prices = await NBAGamesRepo().get_past_teams_matchups_price_series(
            session, guest_team, host_team, market_type
        )

    game_data: dict[str, dict[str, dict[int, dict[str, Decimal]]]] = {}
    for game_id, game_date, ts, g_buy, g_sell, h_buy, h_sell in raw_prices:
        if game_id not in game_data:
            game_data[game_id] = {"date": game_date.isoformat(), "prices": {}}

        game_data[game_id]["prices"][ts] = {
            "guest_buy": g_buy,
            "guest_sell": g_sell,
            "host_buy": h_buy,
            "host_sell": h_sell,
        }
    return game_data
