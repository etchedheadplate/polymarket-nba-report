from typing import Any

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import NBAGamesModel, NBAMarketsModel, NBAPricesModel
from src.service.domain import NBATeamSide
from src.service.schemas import GamesSeriesQuery


class NBAGamesRepo:
    async def get_games_series(self, session: AsyncSession, query: GamesSeriesQuery) -> list[Any]:

        base_conditions = [
            NBAGamesModel.game_status == query.game_status,
            NBAMarketsModel.market_type == query.market_type,
        ]

        if query.team_side == NBATeamSide.GUEST:
            base_conditions.append(NBAGamesModel.guest_team == query.team.name)
        elif query.team_side == NBATeamSide.HOST:
            base_conditions.append(NBAGamesModel.host_team == query.team.name)
        else:
            base_conditions.append(
                or_(NBAGamesModel.guest_team == query.team.name, NBAGamesModel.host_team == query.team.name)
            )

        if query.team_vs:
            if query.team_side == NBATeamSide.GUEST:
                base_conditions.append(
                    and_(NBAGamesModel.guest_team == query.team.name, NBAGamesModel.host_team == query.team_vs.name)
                )
            elif query.team_side == NBATeamSide.HOST:
                base_conditions.append(
                    and_(NBAGamesModel.guest_team == query.team_vs.name, NBAGamesModel.host_team == query.team.name)
                )
            else:
                base_conditions.append(
                    or_(
                        and_(
                            NBAGamesModel.guest_team == query.team.name, NBAGamesModel.host_team == query.team_vs.name
                        ),
                        and_(
                            NBAGamesModel.guest_team == query.team_vs.name, NBAGamesModel.host_team == query.team.name
                        ),
                    )
                )

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
