from decimal import Decimal

from pydantic import BaseModel, PrivateAttr, computed_field

from src.service.domain import NBATeamSide
from src.service.reports.schemas import ReportItem, ReportQuery


class PriceWindowQuery(ReportQuery):
    window_start: Decimal | None = None
    window_end: Decimal | None = None


class WindowSegment(BaseModel):
    start_price: Decimal
    start_ts: int
    end_price: Decimal
    end_ts: int


class PriceWindowItem(ReportItem):
    _window_segs: dict[NBATeamSide, list[WindowSegment]] | None = PrivateAttr(default=None)

    @computed_field
    @property
    def window_segs(self) -> dict[NBATeamSide, list[WindowSegment]] | None:
        return self._window_segs
