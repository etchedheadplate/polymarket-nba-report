from decimal import Decimal

from pydantic import BaseModel

from src.service.domain import GameStatus
from src.service.schemas import BaseQuery, TeamRequiredQuery


class ReportQuery(BaseQuery, TeamRequiredQuery):
    game_status: GameStatus = GameStatus.FINISHED


class PriceSnapshot(BaseModel):
    timestamp: int
    guest_price: Decimal | None
    host_price: Decimal | None


class ReportItem(BaseModel):
    guest_team: str
    host_team: str
    price_series: list[PriceSnapshot]
