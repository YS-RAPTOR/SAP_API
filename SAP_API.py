import enum
import win32gui
import win32process

from PIL import Image
from pywinauto.application import Application
from pywinauto.controls.hwndwrapper import HwndWrapper
from time import sleep
from HandleConfig import init
from dataclasses import dataclass

WIDTH = 1280
HEIGHT = 720

ARGS = f"-screen-width {WIDTH} -screen-height {HEIGHT} -screen-fullscreen 0"

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

class SAP_API:
    sapPath : str
    app: Application
    SAP : HwndWrapper
    state: GameState

    def __init__(self, args: str = ARGS):
        sapPath = init()
        self.app = Application().start(f"{sapPath} {args}")
        self.SAP = self.app.SuperAutoPets.wrapper_object()
        
    def __del__(self):
        self.app.kill()

    def GetCapture(self) -> Image:
        self.SAP.set_focus()
        sleep(0.1)
        return self.SAP.capture_as_image()

    def GetHandler(pid: int) -> int:
        handles = []

        def WindowCallback(handle, handles):
            if win32process.GetWindowThreadProcessId(handle)[1]== pid:
                handles.append(handle)

        def print(hwnd, extra):
            print(win32gui.GetWindowText(hwnd))

        win32gui.EnumWindows(WindowCallback, handles)

        return handles[0]
        

    def GetGameState(self) -> GameState:
        pass

    def PerformAction(self, action: ActionTypes, startSlot: int, endSlot: int):
        pass

    

    
    


    



if __name__ == '__main__':
    sap = SAP_API("")