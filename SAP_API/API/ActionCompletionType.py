from enum import Enum, auto

class CompletionType (Enum):
    NEXT_STATE = auto()
    NO_CHANGES = auto()
    NO_CHANGES_AND_NOT_INITIAL_STATE = auto()