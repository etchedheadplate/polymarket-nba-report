from datetime import date
from decimal import Decimal

from pydantic import BaseModel, PositiveInt, PrivateAttr, computed_field, field_validator

from src.service.schemas import ReportItem, ReportQuery


class QuoteSeriesQuery(ReportQuery): ...


class HalftimeSegment(BaseModel):
    start_ts: int
    end_ts: int


class UnderdogSegment(BaseModel):
    team: str
    start_ts: int
    end_ts: int
    min_price: Decimal
    min_ts: int


class QuoteSeriesItem(ReportItem):
    game_id: PositiveInt
    game_date: date
    market_type: str
    guest_score: PositiveInt | None
    host_score: PositiveInt | None

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
