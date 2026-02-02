from datetime import date
from decimal import Decimal

from pydantic import BaseModel, PositiveInt, computed_field, field_validator

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


class UnderdogSegment(BaseModel):
    team: str
    start_ts: int
    end_ts: int
    min_price: Decimal
    min_price_ts: int


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

    _halftime_ts: tuple[int, int] | None = None
    _underdog_segs: list[UnderdogSegment] | None = None

    @computed_field
    @property
    def halftime_ts(self) -> tuple[int, int] | None:
        return self._halftime_ts

    @computed_field
    @property
    def underdog_segs(self) -> list[UnderdogSegment] | None:
        return self._underdog_segs
