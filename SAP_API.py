import enum
import cv2
import numpy as np
import pytesseract as pyt
import PIL.Image as PILImage

from PIL.Image import Image
from pywinauto.application import Application
from pywinauto.controls.hwndwrapper import HwndWrapper
from time import sleep
from HandleConfig import init
from dataclasses import dataclass

WIDTH = 1280
HEIGHT = 720

# 70/40

GOLD_CROP = (56,21,107,60)
LIVES_CROP = (168,21,212,60)
ROUNDS_CROP = (424,21,492,60)
COST_CROP = (200,370,226,388)

TESSERACT_CONFIG = '--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789'


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
    
    fullGame: Image
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

    def __str__(self) -> str:
        return f"Gold: {self.gold}, Lives: {self.lives}, Round: {self.round}, Cost: {self.cost}"
        
    
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

    def GetGameState(self) -> GameState:
        # Capture the game
        capture = self.GetCapture()
        
        # Crop the game characters for OCR
        gold = capture.crop(GOLD_CROP)
        lives = capture.crop(LIVES_CROP)
        rounds = capture.crop(ROUNDS_CROP)
        costs = capture.crop(COST_CROP)

        # Preprocess the images for OCR
        gold = self.PreprocessForOCR(gold)
        lives = self.PreprocessForOCR(lives)
        rounds = self.PreprocessForOCR(rounds)

        # Setup Game State
        state = GameState()
        state.fullGame = capture

        # Use OCR
        state.gold = self.ConvertToInt(gold, True)
        state.lives = self.ConvertToInt(lives)
        state.round = self.ConvertToInt(rounds)
        state.cost = self.ConvertToInt(costs)

        return state



    def PerformAction(self, action: ActionTypes, startSlot: int, endSlot: int):
        pass

    

    @staticmethod
    def Crop(img: Image):
        horizontalToCrop = img.size[0] - WIDTH
        verticalToCrop = img.size[1] - HEIGHT

        left = horizontalToCrop // 2
        right = left + WIDTH

        top = verticalToCrop - left
        bottom = HEIGHT + top

        return img.crop((left, top, right, bottom))

    @staticmethod
    def PreprocessForOCR(img: Image):
        img = img.convert("L")
        img = img.point(lambda p: 255 if p < 128 else 0)
        img = cv2.floodFill(np.array(img), None, (0,0), 255)
        img = PILImage.fromarray(img[1])
        return img

    @staticmethod
    def ConvertToInt(img: Image, ignoreErrors = False):
        temp = pyt.image_to_string(img, config=TESSERACT_CONFIG)
        if(temp != ""):
            return int(temp)
        elif(ignoreErrors):
            return 0
        else:
            raise Exception("OCR returned nothing")
    



if __name__ == '__main__':
    sap = SAP_API("")

    while True:
        input()
        print(sap.GetGameState())

