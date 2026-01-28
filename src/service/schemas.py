from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class MatchupPriceEntry(BaseModel):
    timestamp: int
    guest_buy: Decimal | None
    guest_sell: Decimal | None
    host_buy: Decimal | None
    host_sell: Decimal | None


class GameMatchup(BaseModel):
    game_id: int
    game_date: date
    market_type: str
    guest_team: str
    host_team: str
    guest_score: int | None
    host_score: int | None
    prices: list[MatchupPriceEntry]
