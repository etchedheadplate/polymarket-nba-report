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


class NBATeamSide(StrEnum):
    GUEST = "guest"
    HOST = "host"


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
class NBATeamColor:
    PHI = {"guest": Color.DARK_BLUE, "host": Color.LIGHT_RED}
    MIL = {"guest": Color.DARK_GREEN, "host": Color.LIGHT_GOLD}
    CHI = {"guest": Color.DARK_GREY, "host": Color.LIGHT_RED}
    CLE = {"guest": Color.DARK_RED, "host": Color.LIGHT_RED}
    BOS = {"guest": Color.DARK_GREEN, "host": Color.LIGHT_GOLD}
    LAC = {"guest": Color.DARK_BLUE, "host": Color.LIGHT_RED}
    MEM = {"guest": Color.DARK_BLUE, "host": Color.LIGHT_BLUE}
    ATL = {"guest": Color.DARK_GREY, "host": Color.LIGHT_RED}
    MIA = {"guest": Color.DARK_RED, "host": Color.LIGHT_ORANGE}
    CHA = {"guest": Color.DARK_BLUE, "host": Color.LIGHT_BLUE}
    UTA = {"guest": Color.DARK_PURPLE, "host": Color.LIGHT_BLUE}
    SAC = {"guest": Color.DARK_PURPLE, "host": Color.LIGHT_GREY}
    NYK = {"guest": Color.DARK_BLUE, "host": Color.LIGHT_ORANGE}
    LAL = {"guest": Color.DARK_PURPLE, "host": Color.LIGHT_YELLOW}
    ORL = {"guest": Color.DARK_BLUE, "host": Color.LIGHT_BLUE}
    DAL = {"guest": Color.DARK_BLUE, "host": Color.LIGHT_BLUE}
    BKN = {"guest": Color.DARK_GREY, "host": Color.LIGHT_GREY}
    DEN = {"guest": Color.DARK_BLUE, "host": Color.LIGHT_YELLOW}
    IND = {"guest": Color.DARK_BLUE, "host": Color.LIGHT_YELLOW}
    NOP = {"guest": Color.DARK_BLUE, "host": Color.LIGHT_RED}
    DET = {"guest": Color.DARK_BLUE, "host": Color.LIGHT_RED}
    TOR = {"guest": Color.DARK_GREY, "host": Color.LIGHT_RED}
    HOU = {"guest": Color.DARK_GREY, "host": Color.LIGHT_RED}
    SAS = {"guest": Color.DARK_GREY, "host": Color.LIGHT_GREY}
    PHX = {"guest": Color.DARK_PURPLE, "host": Color.LIGHT_ORANGE}
    OKC = {"guest": Color.DARK_BLUE, "host": Color.LIGHT_RED}
    MIN = {"guest": Color.DARK_BLUE, "host": Color.LIGHT_GREY}
    POR = {"guest": Color.DARK_GREY, "host": Color.LIGHT_RED}
    GSW = {"guest": Color.DARK_BLUE, "host": Color.LIGHT_YELLOW}
    WAS = {"guest": Color.DARK_BLUE, "host": Color.LIGHT_RED}


class MarketType(StrEnum):  # adjusted for needed types
    # assists = "assists"
    # first_half_moneyline = "first_half_moneyline"
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
