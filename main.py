import asyncio

from src.service.domain import NBATeam
from src.service.tasks import get_team_games, get_teams_matchups, get_teams_matchups_data


async def main():
    guest_team = NBATeam.BOS
    host_team = NBATeam.NYK

    games = await get_team_games(guest_team)
    matchups = await get_teams_matchups(guest_team, host_team)
    prices = await get_teams_matchups_data(guest_team, host_team)

    print(len(games), len(matchups) == len(prices))


if __name__ == "__main__":
    asyncio.run(main())
