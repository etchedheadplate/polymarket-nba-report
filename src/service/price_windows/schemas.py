from decimal import Decimal

from pydantic import BaseModel, PrivateAttr, computed_field

from src.service.domain import NBATeamSide
from src.service.schemas import PriceSnapshot, ReportQuery


class PriceWindowQuery(ReportQuery):
    price: Decimal | None = None
    window_start: Decimal | None = None
    window_end: Decimal | None = None


class WindowSegment(BaseModel):
    start_price: Decimal
    start_ts: int
    end_price: Decimal
    end_ts: int


class PriceWindowItem(BaseModel):
    guest_team: str
    host_team: str
    price_series: list[PriceSnapshot]
    _window_segs: dict[NBATeamSide, list[WindowSegment]] | None = PrivateAttr(default=None)

    @computed_field
    @property
    def window_segs(self) -> dict[NBATeamSide, list[WindowSegment]] | None:
        return self._window_segs
