from typing import Any

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import NBAGamesModel, NBAMarketsModel, NBAPricesModel
from src.service.domain import NBATeamSide
from src.service.schemas import GamesSeriesQuery


class NBAGamesRepo:
    async def get_games_series(self, session: AsyncSession, query: GamesSeriesQuery) -> list[Any]:

        stmt = (
            select(
                NBAGamesModel.id,
                NBAGamesModel.game_date,
                NBAGamesModel.guest_team,
                NBAGamesModel.host_team,
                NBAGamesModel.guest_score,
                NBAGamesModel.host_score,
                NBAMarketsModel.market_type,
                NBAPricesModel.timestamp,
                NBAPricesModel.price_guest_buy,
                NBAPricesModel.price_guest_sell,
                NBAPricesModel.price_host_buy,
                NBAPricesModel.price_host_sell,
            )
            .join(NBAMarketsModel, NBAPricesModel.market_id == NBAMarketsModel.id)
            .join(NBAGamesModel, NBAMarketsModel.event_id == NBAGamesModel.id)
        )

        conditions = [NBAGamesModel.game_status == query.game_status, NBAMarketsModel.market_type == query.market_type]

        if query.team_side == NBATeamSide.GUEST:
            conditions.append(NBAGamesModel.guest_team == query.team.name)
        elif query.team_side == NBATeamSide.HOST:
            conditions.append(NBAGamesModel.host_team == query.team.name)
        elif not query.team_side:
            conditions.append(
                or_(NBAGamesModel.guest_team == query.team.name, NBAGamesModel.host_team == query.team.name)
            )

        if query.team_vs:
            if query.team_side == NBATeamSide.GUEST:
                conditions.append(
                    and_(NBAGamesModel.guest_team == query.team.name, NBAGamesModel.host_team == query.team_vs.name)
                )
            elif query.team_side == NBATeamSide.HOST:
                conditions.append(
                    and_(NBAGamesModel.guest_team == query.team_vs.name, NBAGamesModel.host_team == query.team.name)
                )
            else:
                conditions.append(
                    or_(
                        and_(
                            NBAGamesModel.guest_team == query.team.name, NBAGamesModel.host_team == query.team_vs.name
                        ),
                        and_(
                            NBAGamesModel.guest_team == query.team_vs.name, NBAGamesModel.host_team == query.team.name
                        ),
                    )
                )

        stmt = stmt.where(*conditions)

        if query.limit is not None:
            stmt = stmt.limit(query.limit)

        result = await session.execute(stmt)
        return list(result.all())
