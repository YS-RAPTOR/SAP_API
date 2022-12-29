import enum
import subprocess
import win32gui

from HandleConfig import init
from dataclasses import dataclass

class ActionTypes(enum.Enum):
    """Action types for the game"""
    SET = 1
    SELL = 2
    FREEZE = 3
    ROLL = 5
    END = 6

class Results(enum.Enum):
    """Results of the game"""
    LOSE = -1
    DRAW = 0
    WIN = 1

@dataclass
class GameState():
    """Game state"""
    # TODO: Add the game state variables
    # 5 animal slots, 5 shop slots, 2 food slots
    # Total slots is 12 slots. Store as Array of images
    gold: int
    lives: int
    round: int
    cost: int


def get_game_state() -> GameState:
    pass

def perform_action(action: ActionTypes, slot: int):
    pass

def main():
    # Initialize the SAP Variables
    sap_path = init()
    # Run SAP
    rand = subprocess.Popen(sap_path)







if __name__ == '__main__':
    main()
