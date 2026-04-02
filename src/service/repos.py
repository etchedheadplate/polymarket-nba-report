from typing import Any

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session
from sqlalchemy.sql.elements import ColumnElement

from src.database.models import NBAGamesModel, NBAMarketsModel, NBAPricesModel
from src.service.domain import NBATeam, NBATeamSide
from src.service.reports.schemas import ReportQuery
from src.service.schemas import EventsFutureQuery, EventsPastQuery


class NBAGamesRepo:
    def _build_team_conditions(
        self, team: NBATeam, team_vs: NBATeam | None, team_side: NBATeamSide | None
    ) -> ColumnElement[bool]:
        if not team_vs:
            if team_side == NBATeamSide.GUEST:
                return NBAGamesModel.guest_team == team.name
            elif team_side == NBATeamSide.HOST:
                return NBAGamesModel.host_team == team.name
            else:
                return or_(NBAGamesModel.guest_team == team.name, NBAGamesModel.host_team == team.name)

        else:
            vs = team_vs.name

            if team_side == NBATeamSide.GUEST:
                return and_(NBAGamesModel.guest_team == team.name, NBAGamesModel.host_team == vs)
            elif team_side == NBATeamSide.HOST:
                return and_(NBAGamesModel.guest_team == vs, NBAGamesModel.host_team == team.name)
            else:
                return or_(
                    and_(NBAGamesModel.guest_team == team.name, NBAGamesModel.host_team == vs),
                    and_(NBAGamesModel.guest_team == vs, NBAGamesModel.host_team == team.name),
                )

    def get_game_events(self, session: Session, query: EventsPastQuery | EventsFutureQuery) -> list[Any]:
        base_conditions: list[ColumnElement[bool]] = [NBAGamesModel.game_date.between(query.start_date, query.end_date)]
        if query.team:
            team_conditions = self._build_team_conditions(query.team, query.team_vs, query.team_side)
            base_conditions.append(team_conditions)

        stmt = select(
            NBAGamesModel.id,
            NBAGamesModel.game_date,
            NBAGamesModel.guest_team,
            NBAGamesModel.host_team,
            NBAGamesModel.guest_score,
            NBAGamesModel.host_score,
            NBAGamesModel.game_status,
        ).where(
            *base_conditions,
        )
        result = session.execute(stmt)
        return list(result.all())

    def get_games_with_prices(self, session: Session, query: ReportQuery, team_conditions: bool = True) -> list[Any]:
        base_conditions = [NBAGamesModel.game_status == query.game_status]

        if team_conditions:
            additional_conditions = self._build_team_conditions(query.team, query.team_vs, query.team_side)
            base_conditions.append(additional_conditions)

        if query.limit is None:
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
                    *base_conditions,
                    NBAMarketsModel.market_type == query.market_type,
                )
                .order_by(
                    NBAGamesModel.game_date.desc(),
                    NBAPricesModel.timestamp.asc(),
                )
            )

        else:
            games_subq = (
                select(NBAGamesModel.id)
                .where(*base_conditions)
                .order_by(NBAGamesModel.game_date.desc())
                .limit(query.limit)
                .subquery()
            )

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
                .join(games_subq, games_subq.c.id == NBAGamesModel.id)
                .join(NBAMarketsModel, NBAMarketsModel.event_id == NBAGamesModel.id)
                .join(NBAPricesModel, NBAPricesModel.market_id == NBAMarketsModel.id)
                .where(NBAMarketsModel.market_type == query.market_type)
                .order_by(
                    NBAGamesModel.game_date.desc(),
                    NBAPricesModel.timestamp.asc(),
                )
            )

        result = session.execute(stmt)
        return list(result.all())
