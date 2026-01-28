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


class Colors(StrEnum):
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
    PHI = {"guest": Colors.LIGHT_RED, "host": Colors.DARK_BLUE}
    MIL = {"guest": Colors.LIGHT_GOLD, "host": Colors.DARK_GREEN}
    CHI = {"guest": Colors.LIGHT_RED, "host": Colors.DARK_GREY}
    CLE = {"guest": Colors.LIGHT_RED, "host": Colors.DARK_RED}
    BOS = {"guest": Colors.LIGHT_GOLD, "host": Colors.DARK_GREEN}
    LAC = {"guest": Colors.LIGHT_RED, "host": Colors.DARK_BLUE}
    MEM = {"guest": Colors.LIGHT_BLUE, "host": Colors.DARK_BLUE}
    ATL = {"guest": Colors.LIGHT_RED, "host": Colors.DARK_GREY}
    MIA = {"guest": Colors.LIGHT_ORANGE, "host": Colors.DARK_RED}
    CHA = {"guest": Colors.LIGHT_BLUE, "host": Colors.DARK_BLUE}
    UTA = {"guest": Colors.LIGHT_BLUE, "host": Colors.DARK_PURPLE}
    SAC = {"guest": Colors.LIGHT_GREY, "host": Colors.DARK_PURPLE}
    NYK = {"guest": Colors.LIGHT_ORANGE, "host": Colors.DARK_BLUE}
    LAL = {"guest": Colors.LIGHT_YELLOW, "host": Colors.DARK_PURPLE}
    ORL = {"guest": Colors.LIGHT_BLUE, "host": Colors.DARK_BLUE}
    DAL = {"guest": Colors.LIGHT_BLUE, "host": Colors.DARK_BLUE}
    BKN = {"guest": Colors.LIGHT_GREY, "host": Colors.DARK_GREY}
    DEN = {"guest": Colors.LIGHT_YELLOW, "host": Colors.DARK_BLUE}
    IND = {"guest": Colors.LIGHT_YELLOW, "host": Colors.DARK_BLUE}
    NOP = {"guest": Colors.LIGHT_RED, "host": Colors.DARK_BLUE}
    DET = {"guest": Colors.LIGHT_RED, "host": Colors.DARK_BLUE}
    TOR = {"guest": Colors.LIGHT_RED, "host": Colors.DARK_GREY}
    HOU = {"guest": Colors.LIGHT_RED, "host": Colors.DARK_GREY}
    SAS = {"guest": Colors.LIGHT_GREY, "host": Colors.DARK_GREY}
    PHX = {"guest": Colors.LIGHT_ORANGE, "host": Colors.DARK_PURPLE}
    OKC = {"guest": Colors.LIGHT_RED, "host": Colors.DARK_BLUE}
    MIN = {"guest": Colors.LIGHT_GREY, "host": Colors.DARK_BLUE}
    POR = {"guest": Colors.LIGHT_RED, "host": Colors.DARK_GREY}
    GSW = {"guest": Colors.LIGHT_YELLOW, "host": Colors.DARK_BLUE}
    WAS = {"guest": Colors.LIGHT_RED, "host": Colors.DARK_BLUE}


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
