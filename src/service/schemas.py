from datetime import date
from decimal import Decimal

from pydantic import BaseModel, PositiveInt, field_validator

from src.service.domain import GameStatus, MarketType, NBATeam, NBATeamSide


class GameSeriesQuery(BaseModel):
    game_status: GameStatus = GameStatus.FINISHED
    market_type: MarketType = MarketType.moneyline
    limit: PositiveInt | None = None
    team: NBATeam
    team_vs: NBATeam | None = None
    team_side: NBATeamSide | None = None


class GameSeriesPriceResponse(BaseModel):
    timestamp: int
    guest_price: Decimal | None
    host_price: Decimal | None


class GameSeriesResponse(BaseModel):
    game_id: PositiveInt
    game_date: date
    market_type: str
    guest_team: str
    host_team: str
    guest_score: PositiveInt | None
    host_score: PositiveInt | None
    prices: list[GameSeriesPriceResponse]

    @field_validator("market_type", mode="before")
    @classmethod
    def normalize_market_type(cls, v: str) -> str:
        return v.replace("_", " ").title()
