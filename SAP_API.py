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


def GetGameState() -> GameState:
    pass

def PerformAction(action: ActionTypes, startSlot: int, endSlot: int):
    pass

def GetHandler(pid: int) -> int:
    
    handles = []

    def WindowCallback(handle, handles):
        if win32process.GetWindowThreadProcessId(handle)[1]== pid:
            handles.append(handle)

    win32gui.EnumWindows(WindowCallback, handles)

    return handles[0]

def main():
    # Initialize the SAP Variables
    sapPath = init() + " " + ARGS

    # Run SAP
    sapPID = subprocess.Popen(sapPath).pid
    sleep(5)
    
    # Get the window handle
    hwnd = GetHandler(sapPID)

    # Change the line below depending on whether you want the whole window
    # or just the client area. 
    #left, top, right, bot = win32gui.GetClientRect(hwnd)
    left, top, right, bot = win32gui.GetWindowRect(hwnd)
    w = right - left
    h = bot - top
    hwnd_dc = win32gui.GetWindowDC(hwnd)
    mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
    save_dc = mfc_dc.CreateCompatibleDC()
    save_bit_map = win32ui.CreateBitmap()
    save_bit_map.CreateCompatibleBitmap(mfc_dc, w, h)
    save_dc.SelectObject(save_bit_map)
    result = windll.user32.PrintWindow(hwnd, save_dc.GetSafeHdc(), 1)
    if result == 0:
        return False
    bmpinfo = save_bit_map.GetInfo()
    bmpstr = save_bit_map.GetBitmapBits(True)
    img = Image.frombuffer(
        'RGB',
        (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
        bmpstr, 'raw', 'BGRX', 0, 1)
    win32gui.DeleteObject(save_bit_map.GetHandle())
    save_dc.DeleteDC()
    mfc_dc.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwnd_dc)

    if result == 1:
        #PrintWindow Succeeded
        img.save("test.png")
    


    



if __name__ == '__main__':
    main()
