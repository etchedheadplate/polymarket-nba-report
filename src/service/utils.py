import math
from decimal import Decimal

from src.service.schemas import ReportItem


def calculate_standard_deviation(values: list[Decimal]) -> float:
    if not values:
        return 0
    mean = sum(values) / len(values)
    return math.sqrt(sum((float(v) - float(mean)) ** 2 for v in values) / len(values))


def normalize_prices(buy: Decimal | None, sell: Decimal | None) -> Decimal | None:
    if buy is not None and sell is not None:
        return (buy + sell) / 2
    return buy or sell


def is_matching_game(game: ReportItem, team: str, team_vs: str | None = None) -> bool:
    guest = game.guest_team
    host = game.host_team
    if team not in (guest, host):
        return False
    if team_vs:
        return (guest == team and host == team_vs) or (guest == team_vs and host == team)
    return True
