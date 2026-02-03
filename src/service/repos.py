from typing import Any

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import NBAGamesModel, NBAMarketsModel, NBAPricesModel
from src.service.domain import NBATeamSide
from src.service.schemas import ReportQuery


class NBAGamesRepo:
    async def get_games_series(self, session: AsyncSession, query: ReportQuery) -> list[Any]:

        def build_team_conditions(query: ReportQuery):
            team = query.team.name

            if not query.team_vs:
                if query.team_side == NBATeamSide.GUEST:
                    return NBAGamesModel.guest_team == team
                elif query.team_side == NBATeamSide.HOST:
                    return NBAGamesModel.host_team == team
                else:
                    return or_(NBAGamesModel.guest_team == team, NBAGamesModel.host_team == team)

            else:
                vs = query.team_vs.name

                if query.team_side == NBATeamSide.GUEST:
                    return and_(NBAGamesModel.guest_team == team, NBAGamesModel.host_team == vs)
                elif query.team_side == NBATeamSide.HOST:
                    return and_(NBAGamesModel.guest_team == vs, NBAGamesModel.host_team == team)
                else:
                    return or_(
                        and_(NBAGamesModel.guest_team == team, NBAGamesModel.host_team == vs),
                        and_(NBAGamesModel.guest_team == vs, NBAGamesModel.host_team == team),
                    )

        base_conditions = [
            NBAGamesModel.game_status == query.game_status,
            NBAMarketsModel.market_type == query.market_type,
            build_team_conditions(query),
        ]

        games_ids_stmt = (
            select(NBAGamesModel.id)
            .join(NBAMarketsModel, NBAMarketsModel.event_id == NBAGamesModel.id)
            .where(*base_conditions)
            .order_by(NBAGamesModel.game_date.desc())
        )

        if query.limit is not None:
            games_ids_stmt = games_ids_stmt.limit(query.limit)

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
            .join(NBAMarketsModel, NBAMarketsModel.event_id == NBAGamesModel.id)
            .join(NBAPricesModel, NBAPricesModel.market_id == NBAMarketsModel.id)
            .where(
                NBAGamesModel.id.in_(games_ids_stmt),
                NBAMarketsModel.market_type == query.market_type,
            )
            .order_by(
                NBAGamesModel.game_date.desc(),
                NBAPricesModel.timestamp.asc(),
            )
        )

        result = await session.execute(stmt)
        return list(result.all())
