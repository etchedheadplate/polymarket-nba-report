from decimal import Decimal

from src.database.connection import async_session_maker
from src.service.domain import MarketType, NBATeam
from src.service.repos import NBAGamesRepo
from src.service.schemas import GameMatchup, MatchupPriceEntry


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
) -> dict[int, GameMatchup]:
    async with async_session_maker() as session:
        raw_games_data = await NBAGamesRepo().get_past_teams_matchups_series(
            session, guest_team, host_team, market_type
        )

    games_data_dict: dict[int, GameMatchup] = {}
    for game_id, game_date, guest_score, host_score, ts, g_buy, g_sell, h_buy, h_sell in raw_games_data:
        if game_id not in games_data_dict:
            games_data_dict[game_id] = GameMatchup(
                game_id=game_id,
                game_date=game_date,
                market_type=market_type,
                guest_team=guest_team.name,
                host_team=host_team.name,
                guest_score=guest_score,
                host_score=host_score,
                prices=[],
            )

        def normalize(buy: Decimal | None, sell: Decimal | None) -> Decimal | None:
            if buy is not None and sell is not None:
                return (buy + sell) / 2
            return buy or sell

        games_data_dict[game_id].prices.append(
            MatchupPriceEntry(
                timestamp=ts,
                guest_buy=normalize(g_buy, g_sell),
                guest_sell=None,
                host_buy=normalize(h_buy, h_sell),
                host_sell=None,
            )
        )

    return games_data_dict
