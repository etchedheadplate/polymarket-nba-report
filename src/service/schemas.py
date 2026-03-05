from pydantic import BaseModel, PositiveInt

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
    team: NBATeam | None
