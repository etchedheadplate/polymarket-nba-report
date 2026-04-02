from datetime import date

from pydantic import BaseModel, PositiveInt, field_validator

from src.service.domain import MarketType, NBATeam, NBATeamSide


class BaseQuery(BaseModel):
    market_type: MarketType = MarketType.moneyline
    limit: PositiveInt | None = None


class TeamQuery(BaseModel):
    team_vs: NBATeam | None = None
    team_side: NBATeamSide | None = None


class TeamRequiredQuery(TeamQuery):
    team: NBATeam


class TeamOptionalQuery(TeamQuery):
    team: NBATeam | None = None


class EventsQuery(BaseModel):
    start_date: date
    end_date: date

    @field_validator("start_date", "end_date", mode="before")
    @classmethod
    def parse_date(cls, value: str):
        if isinstance(value, date):
            return value
        return date.fromisoformat(value)


class EventsPastQuery(EventsQuery, TeamRequiredQuery): ...


class EventsFutureQuery(EventsQuery, TeamOptionalQuery): ...
