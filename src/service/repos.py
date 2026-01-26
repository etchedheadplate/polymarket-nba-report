from typing import Any

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import NBAGamesModel, NBAMarketsModel, NBAPricesModel
from src.service.domain import GameStatus, MarketType, NBATeam


class NBAGamesRepo:
    async def get_past_team_games_ids(self, session: AsyncSession, team: NBATeam) -> list[int]:
        stmt = select(NBAGamesModel.id).where(
            and_(
                NBAGamesModel.game_status == GameStatus.FINISHED,
                or_(NBAGamesModel.guest_team == team.name, NBAGamesModel.host_team == team.name),
            )
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def get_past_teams_matchups_ids(
        self, session: AsyncSession, guest_team: NBATeam, host_team: NBATeam
    ) -> list[int]:
        stmt = select(NBAGamesModel.id).where(
            and_(
                NBAGamesModel.game_status == GameStatus.FINISHED,
                NBAGamesModel.guest_team == guest_team.name,
                NBAGamesModel.host_team == host_team.name,
            )
        )

        result = await session.execute(stmt)
        return list(result.scalars())

    async def get_past_teams_matchups_price_series(
        self, session: AsyncSession, guest_team: NBATeam, host_team: NBATeam, market_type: MarketType
    ) -> list[Any]:

        stmt = (
            select(
                NBAGamesModel.id,
                NBAGamesModel.game_date,
                NBAPricesModel.timestamp,
                NBAPricesModel.price_guest_buy,
                NBAPricesModel.price_guest_sell,
                NBAPricesModel.price_host_buy,
                NBAPricesModel.price_host_sell,
            )
            .join(NBAMarketsModel, NBAPricesModel.market_id == NBAMarketsModel.id)
            .join(NBAGamesModel, NBAMarketsModel.event_id == NBAGamesModel.id)
            .where(
                and_(
                    NBAGamesModel.game_status == GameStatus.FINISHED,
                    NBAGamesModel.guest_team == guest_team.name,
                    NBAGamesModel.host_team == host_team.name,
                    NBAMarketsModel.market_type == market_type,
                )
            )
        )

        result = await session.execute(stmt)
        return list(result.all())
