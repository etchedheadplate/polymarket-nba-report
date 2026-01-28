from dataclasses import dataclass
from enum import StrEnum


class NBATeam(StrEnum):
    PHI = "76ers"
    MIL = "Bucks"
    CHI = "Bulls"
    CLE = "Cavaliers"
    BOS = "Celtics"
    LAC = "Clippers"
    MEM = "Grizzlies"
    ATL = "Hawks"
    MIA = "Heat"
    CHA = "Hornets"
    UTA = "Jazz"
    SAC = "Kings"
    NYK = "Knicks"
    LAL = "Lakers"
    ORL = "Magic"
    DAL = "Mavericks"
    BKN = "Nets"
    DEN = "Nuggets"
    IND = "Pacers"
    NOP = "Pelicans"
    DET = "Pistons"
    TOR = "Raptors"
    HOU = "Rockets"
    SAS = "Spurs"
    PHX = "Suns"
    OKC = "Thunder"
    MIN = "Timberwolves"
    POR = "Blazers"
    GSW = "Warriors"
    WAS = "Wizards"


class Color(StrEnum):
    LIGHT_RED = "#ff595e"
    LIGHT_BLUE = "#00cecb"
    LIGHT_GREY = "#ced4da"
    LIGHT_GOLD = "#ffef9f"
    LIGHT_ORANGE = "#f35b04"
    LIGHT_YELLOW = "#f7b801"
    DARK_RED = "#9a031e"
    DARK_BLUE = "#4361ee"
    DARK_GREY = "#6c757d"
    DARK_GREEN = "#0ead69"
    DARK_PURPLE = "#7209b7"


@dataclass
class NBAColor:
    PHI = {"guest": Color.LIGHT_RED, "host": Color.DARK_BLUE}
    MIL = {"guest": Color.LIGHT_GOLD, "host": Color.DARK_GREEN}
    CHI = {"guest": Color.LIGHT_RED, "host": Color.DARK_GREY}
    CLE = {"guest": Color.LIGHT_RED, "host": Color.DARK_RED}
    BOS = {"guest": Color.LIGHT_GOLD, "host": Color.DARK_GREEN}
    LAC = {"guest": Color.LIGHT_RED, "host": Color.DARK_BLUE}
    MEM = {"guest": Color.LIGHT_BLUE, "host": Color.DARK_BLUE}
    ATL = {"guest": Color.LIGHT_RED, "host": Color.DARK_GREY}
    MIA = {"guest": Color.LIGHT_ORANGE, "host": Color.DARK_RED}
    CHA = {"guest": Color.LIGHT_BLUE, "host": Color.DARK_BLUE}
    UTA = {"guest": Color.LIGHT_BLUE, "host": Color.DARK_PURPLE}
    SAC = {"guest": Color.LIGHT_GREY, "host": Color.DARK_PURPLE}
    NYK = {"guest": Color.LIGHT_ORANGE, "host": Color.DARK_BLUE}
    LAL = {"guest": Color.LIGHT_YELLOW, "host": Color.DARK_PURPLE}
    ORL = {"guest": Color.LIGHT_BLUE, "host": Color.DARK_BLUE}
    DAL = {"guest": Color.LIGHT_BLUE, "host": Color.DARK_BLUE}
    BKN = {"guest": Color.LIGHT_GREY, "host": Color.DARK_GREY}
    DEN = {"guest": Color.LIGHT_YELLOW, "host": Color.DARK_BLUE}
    IND = {"guest": Color.LIGHT_YELLOW, "host": Color.DARK_BLUE}
    NOP = {"guest": Color.LIGHT_RED, "host": Color.DARK_BLUE}
    DET = {"guest": Color.LIGHT_RED, "host": Color.DARK_BLUE}
    TOR = {"guest": Color.LIGHT_RED, "host": Color.DARK_GREY}
    HOU = {"guest": Color.LIGHT_RED, "host": Color.DARK_GREY}
    SAS = {"guest": Color.LIGHT_GREY, "host": Color.DARK_GREY}
    PHX = {"guest": Color.LIGHT_ORANGE, "host": Color.DARK_PURPLE}
    OKC = {"guest": Color.LIGHT_RED, "host": Color.DARK_BLUE}
    MIN = {"guest": Color.LIGHT_GREY, "host": Color.DARK_BLUE}
    POR = {"guest": Color.LIGHT_RED, "host": Color.DARK_GREY}
    GSW = {"guest": Color.LIGHT_YELLOW, "host": Color.DARK_BLUE}
    WAS = {"guest": Color.LIGHT_RED, "host": Color.DARK_BLUE}


class MarketType(StrEnum):  # adjusted for needed types
    # assists = "assists"
    first_half_moneyline = "first_half_moneyline"
    # first_half_spreads = "first_half_spreads"
    # first_half_totals = "first_half_totals"
    moneyline = "moneyline"
    # points = "points"
    # rebounds = "rebounds"
    # spreads = "spreads"
    # totals = "totals"


class GameStatus(StrEnum):
    NOT_STARTED = "not_started"
    LIVE = "live"
    FINISHED = "finished"
    CANCELLED = "cancelled"
    SUSPENDED = "suspended"
    UNKNOWN = "unknown"


GAME_STATUS_NORMALIZATION_MAP = {
    "NS": GameStatus.NOT_STARTED,
    "SCHED": GameStatus.NOT_STARTED,
    "Q1": GameStatus.LIVE,
    "Q2": GameStatus.LIVE,
    "Q3": GameStatus.LIVE,
    "Q4": GameStatus.LIVE,
    "HT": GameStatus.LIVE,
    "OT": GameStatus.LIVE,
    "OT1": GameStatus.LIVE,
    "OT2": GameStatus.LIVE,
    "FT": GameStatus.FINISHED,
    "FT OT": GameStatus.FINISHED,
    "FT OT1": GameStatus.FINISHED,
    "FT OT2": GameStatus.FINISHED,
    "VFT": GameStatus.FINISHED,
    "CAN": GameStatus.CANCELLED,
    "POST": GameStatus.CANCELLED,
    "SUSP": GameStatus.SUSPENDED,
}


class OrderStatus(StrEnum):
    OPEN = "open"
    PARTIAL = "partial"
    FILLED = "filled"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    UNKNOWN = "unknown"


class OrderSide(StrEnum):
    BUY = "BUY"
    SELL = "SELL"
