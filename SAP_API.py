import enum
import subprocess
import win32ui
import win32gui
import win32process

from time import sleep
from PIL import Image
from ctypes import windll
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
    sapHandler : int
    width: int
    height: int

    def __init__(self, args: str = ARGS):
        # Initialize the SAP Variables
        sapPath = init() + " " + args

        # Run SAP
        sapPID = subprocess.Popen(sapPath).pid
        sleep(5)
        
        # Get the window handle
        self.sapHandler = SAP_API.GetHandler(sapPID)
        
        left, top, right, bot = win32gui.GetWindowRect(self.sapHandler)
        self.width = right - left
        self.height = bot - top

        self.sapHandlerDC = win32gui.GetWindowDC(self.sapHandler)
        self.sapUIDC = win32ui.CreateDCFromHandle(self.sapHandlerDC)
        self.saveDC = self.sapUIDC.CreateCompatibleDC()

        self.bitmap = win32ui.CreateBitmap()
        self.bitmap.CreateCompatibleBitmap(self.sapUIDC, self.width, self.height)

        self.saveDC.SelectObject(self.bitmap)

    def __del__(self):
        win32gui.DeleteObject(self.bitmap.GetHandle())
        self.saveDC.DeleteDC()
        self.sapUIDC.DeleteDC()
        win32gui.ReleaseDC(self.sapHandler, self.sapHandlerDC)

    def GetCapture(self) -> Image:
        result = windll.user32.PrintWindow(self.sapHandler, self.saveDC.GetSafeHdc(), 1)

        if result == 0:
            return None
        
        #PrintWindow Succeeded
        bmpinfo = self.bitmap.GetInfo()
        bmpstr = self.bitmap.GetBitmapBits(True)
        return Image.frombuffer(
            'RGB',
            (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
            bmpstr, 'raw', 'BGRX', 0, 1)

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
    while True:
        sap.GetCapture().save("test.png")
        input("Press Enter to continue...")