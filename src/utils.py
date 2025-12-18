from enum import Enum, auto

START_SO = 1
START_CUM = 0
START_TINH = 1

MAX_SO = 9999
MAX_CUM = 99
MAX_TINH = 64


class SBDLevel(Enum):
    LEVEL_SO = auto()
    LEVEL_CUM = auto()
    LEVEL_TINH = auto()


class Feedback(Enum):
    NEXT = auto()
    FORCE_INCREMENT = auto()
    STOP = auto()


def format_sbd(tinh, cum, so):
    return f"{tinh:02d}{cum:02d}{so:04d}"
