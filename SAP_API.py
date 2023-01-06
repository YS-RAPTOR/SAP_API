import enum
import win32gui
import win32process

import pytesseract as pyt
from PIL import Image
from PIL.Image import *
from pywinauto.application import Application
from pywinauto.controls.hwndwrapper import HwndWrapper
from time import sleep
from HandleConfig import init
from dataclasses import dataclass

WIDTH = 1280
HEIGHT = 720

GOLD_CROP = (56,21,107,60)
LIVES_CROP = (168,21,212,60)
ROUNDS_CROP = (424,21,492,60)

COST_CROP = (200,370,226,388)

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
    # 5 animal slots, 5 shop slots, 2 food slots
    # Total slots is 12 slots. Store as Array of images
    
    animalSlots: list[Image]
    shopSlots: list[Image]
    foodSlots: list[Image]

    gold: int
    lives: int
    round: int
    cost: int

    def __init__(self):
        self.animalSlots = []
        self.shopSlots = []
        self.foodSlots = []

        self.gold = 0
        self.lives = 0
        self.round = 0
        self.cost = 0

    def IsActionValid(self, action: ActionTypes, startSlot: int, endSlot: int) -> bool:
        if(action == ActionTypes.SET):
            # Check if the slot is available
            availableShopSlots = self.GetAvailableShopSlots()
            
            # Check if the start slot is a shop slot
            if(startSlot >= 5):
                # Check if the shop slot is available
                if(not availableShopSlots[startSlot - 5]):
                    return False

            # Check if the end slot is a shop slot
            if(endSlot >= 5):
                # Check if the shop slot is available
                if(not availableShopSlots[endSlot - 5]):
                    return False

        elif(action == ActionTypes.SELL):
            # Check if the slot is a shop slot
            if(startSlot >= 5):
                return False

        elif(action == ActionTypes.FREEZE):
            # Check if the slot is an animal slot
            if(startSlot < 5):
                return False

        return True
    
    def GetAvailableShopSlots(self) -> list[bool]:
        shopSlotsAvailable = [False] * 5
        foodSlotsAvailable = [False] * 2

        if(round >= 1):
            shopSlotsAvailable[0] = True
            shopSlotsAvailable[1] = True
            shopSlotsAvailable[2] = True

            foodSlotsAvailable[0] = True

        if(round >= 3):
            foodSlotsAvailable[1] = True
        
        if(round >= 5):
            shopSlotsAvailable[3] = True

        if(round >= 9):
            shopSlotsAvailable[4] = True

        shopSlotsAvailable.extend(foodSlotsAvailable)

        return shopSlotsAvailable

    def GetSlots(self) -> list[Image]:
        slots = []
        slots.extend(self.animalSlots)
        slots.extend(self.shopSlots)    
        slots.extend(self.foodSlots)
        return slots

    
    
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
        return self.Crop(self.SAP.capture_as_image())

    def Crop(self, img: Image):
        horizontalToCrop = img.size[0] - WIDTH
        verticalToCrop = img.size[1] - HEIGHT

        left = horizontalToCrop // 2
        right = left + WIDTH

        top = verticalToCrop - left
        bottom = HEIGHT + top

        return img.crop((left, top, right, bottom))

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
        capture = self.GetCapture()
        
        gold = capture.crop(GOLD_CROP)
        lives = capture.crop(LIVES_CROP)
        rounds = capture.crop(ROUNDS_CROP)
        costs = capture.crop(COST_CROP)

        state = GameState()


    def PerformAction(self, action: ActionTypes, startSlot: int, endSlot: int):
        pass

    

    
    


    



if __name__ == '__main__':
    sap = SAP_API("")
    input("Press enter to continue...")
    sap.GetGameState()
    