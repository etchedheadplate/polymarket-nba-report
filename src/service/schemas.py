from decimal import Decimal

from pydantic import BaseModel, PositiveInt

from src.service.domain import GameStatus, MarketType, NBATeam, NBATeamSide


class ReportQuery(BaseModel):
    game_status: GameStatus = GameStatus.FINISHED
    market_type: MarketType = MarketType.moneyline
    limit: PositiveInt | None = None
    team: NBATeam
    team_vs: NBATeam | None = None
    team_side: NBATeamSide | None = None


class PriceSnapshot(BaseModel):
    timestamp: int
    guest_price: Decimal | None
    host_price: Decimal | None
