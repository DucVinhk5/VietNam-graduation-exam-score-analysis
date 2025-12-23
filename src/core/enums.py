from enum import Enum, auto

class Feedback(Enum):
    STOP = auto()
    SKIP = auto()
    NEXT = auto()
