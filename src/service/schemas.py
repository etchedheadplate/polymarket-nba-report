from datetime import date
from decimal import Decimal

from pydantic import BaseModel, PositiveInt

from src.service.domain import GameStatus, MarketType, NBATeam, NBATeamSide


class GameReportQuery(BaseModel):
    game_status: GameStatus = GameStatus.FINISHED
    market_type: MarketType = MarketType.moneyline
    limit: PositiveInt | None = None


class GameSeriesQuery(GameReportQuery):
    team: NBATeam
    team_vs: NBATeam | None = None
    team_side: NBATeamSide | None = None


class QuoteSeriesPriceResponse(BaseModel):
    timestamp: int
    guest_price: Decimal | None
    host_price: Decimal | None


class QuoteSeriesResponse(BaseModel):
    game_id: PositiveInt
    game_date: date
    market_type: str
    guest_team: str
    host_team: str
    guest_score: PositiveInt | None
    host_score: PositiveInt | None
    prices: list[QuoteSeriesPriceResponse]
