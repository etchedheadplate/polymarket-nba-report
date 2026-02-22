import math
from decimal import Decimal


def calculate_standard_deviation(values: list[Decimal]) -> float:
    if not values:
        return 0
    mean = sum(values) / len(values)
    return math.sqrt(sum((float(v) - float(mean)) ** 2 for v in values) / len(values))


def normalize_prices(buy: Decimal | None, sell: Decimal | None) -> Decimal | None:
    if buy is not None and sell is not None:
        return (buy + sell) / 2
    return buy or sell
