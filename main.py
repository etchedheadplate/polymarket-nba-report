import asyncio

from src.service.domain import NBATeam, NBATeamSide
from src.service.reports import QuoteSeriesReport
from src.service.schemas import GameSeriesQuery


async def generate_all_combinations():
    for guest in NBATeam:
        query = GameSeriesQuery(team=guest)

        for host in NBATeam:
            query.team_vs = host

            report = QuoteSeriesReport(query)
            await report.make_report()


async def main():
    query = GameSeriesQuery(team=NBATeam.NYK, team_vs=NBATeam.TOR, limit=4, team_side=NBATeamSide.GUEST)
    report = QuoteSeriesReport(query)
    await report.make_report()


if __name__ == "__main__":
    asyncio.run(main())
