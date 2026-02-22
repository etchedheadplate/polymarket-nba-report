from datetime import date
from decimal import Decimal

from pydantic import BaseModel, PositiveInt, PrivateAttr, computed_field, field_validator

from src.service.domain import GameStatus, MarketType, NBATeam, NBATeamSide


class ReportQuery(BaseModel):
    game_status: GameStatus = GameStatus.FINISHED
    market_type: MarketType = MarketType.moneyline
    limit: PositiveInt | None = None
    team: NBATeam
    team_vs: NBATeam | None = None
    team_side: NBATeamSide | None = None
    price: Decimal | None = None
    window_start: Decimal | None = None
    window_end: Decimal | None = None


class PriceSnapshot(BaseModel):
    timestamp: int
    guest_price: Decimal | None
    host_price: Decimal | None


class WindowSegment(BaseModel):
    start_price: Decimal
    start_ts: int
    end_price: Decimal
    end_ts: int


class HalftimeSegment(BaseModel):
    start_ts: int
    end_ts: int


class UnderdogSegment(BaseModel):
    team: str
    start_ts: int
    end_ts: int
    min_price: Decimal
    min_ts: int


class QuoteSeriesItem(BaseModel):
    game_id: PositiveInt
    game_date: date
    market_type: str
    guest_team: str
    host_team: str
    guest_score: PositiveInt | None
    host_score: PositiveInt | None
    price_series: list[PriceSnapshot]

    @field_validator("market_type", mode="before")
    @classmethod
    def normalize_market_type(cls, v: str) -> str:
        return v.replace("_", " ").title()

    _halftime_seg: HalftimeSegment | None = PrivateAttr(default=None)
    _underdog_segs: list[UnderdogSegment] | None = PrivateAttr(default=None)

    @computed_field
    @property
    def halftime_seg(self) -> HalftimeSegment | None:
        return self._halftime_seg

    @computed_field
    @property
    def underdog_segs(self) -> list[UnderdogSegment] | None:
        return self._underdog_segs


class PriceWindowItem(BaseModel):
    guest_team: str
    host_team: str
    price_series: list[PriceSnapshot]
    _window_segs: dict[NBATeamSide, list[WindowSegment]] | None = PrivateAttr(default=None)

    @computed_field
    @property
    def window_segs(self) -> dict[NBATeamSide, list[WindowSegment]] | None:
        return self._window_segs
