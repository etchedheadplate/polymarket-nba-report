import asyncio

from src.service.domain import NBATeam
from src.service.reports import GamesReport
from src.service.schemas import GamesSeriesQuery


async def generate_all_combinations():
    for guest in NBATeam:
        query = GamesSeriesQuery(team=guest)

        for host in NBATeam:
            query.team_vs = host

            report = GamesReport(query)
            await report.make_report()


async def main():
    query = GamesSeriesQuery(team=NBATeam.LAL, team_vs=NBATeam.BOS)
    report = GamesReport(query)
    await report.make_report()


if __name__ == "__main__":
    asyncio.run(main())
