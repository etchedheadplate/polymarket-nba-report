from decimal import Decimal

from pydantic import BaseModel, PositiveInt

from src.service.reports.schemas import ReportItem, ReportQuery


class WinChancesQuery(ReportQuery):
    visited_price: Decimal | None = None
    mins_until_end: PositiveInt


class WindowSegment(BaseModel):
    start_price: Decimal
    start_ts: int
    end_price: Decimal
    end_ts: int


class WinChancesItem(ReportItem): ...
