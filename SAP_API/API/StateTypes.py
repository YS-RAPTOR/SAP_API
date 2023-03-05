from enum import Enum, auto

class StateTypes(Enum):
    NOT_INITIALIZED = auto()
    PRIVACY_POLICY = auto()
    LOGIN = auto()
    NEWS_ANNOUNCEMENTS = auto()
    MENU = auto()
    SETTINGS = auto()
    ARENA_SETTINGS = auto()
    CHOOSE_PACK = auto()
    MENU_WITH_GAME = auto()
    REGISTER_PROMPT = auto()
    CUSTOMIZE_APPEARANCE = auto()
    GAME = auto()
