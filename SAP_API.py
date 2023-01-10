import enum
import cv2
import io
import cv2  
import asyncio
import numpy as np

import pytesseract as pyt
import PIL.Image as PILImage

from time import sleep
from PIL.Image import Image
from selenium import webdriver
from dataclasses import dataclass
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC

# Selenium Tags
RUN_GAME_CLASS_NAME = "load_iframe_btn"
GAME_ID = "game_drop"

# Constants
WIDTH = 1280
HEIGHT = 720

# Crop coordinates
GOLD_CROP = (56,21,107,60)
LIVES_CROP = (168,21,212,60)
ROUNDS_CROP = (424,21,492,60)
COST_CROP = (200,370,226,388)

ANIMAL_SLOTS_START = (300, 130)
ANIMAL_SLOTS_SIZE = (96, 225)

SHOP_SLOTS_START = (303, 380)
SHOP_SLOTS_SIZE = (96, 170)

FOOD_SLOTS_START = (783, 380)

# Click Locations

END_ROUND_BUTTON = (600, 300)
ROLL_BUTTON = (-600, 300)
FREEZE_SELL_BUTTON = (100, 300)

SETTINGS = [(600, -300),
            (-600, -250),
            (0, -300),
            (0, -100),
            (-600, -100),
            (0, -300),
            (-600, 0),
            (0, -300),
            (0, -200), 
            (0, -100), 
            (0, 0), 
            (0, 100), 
            (-600, 300),
            (-500, -200),
            (0, -250),
            (0, 0)]

# Configs
TESSERACT_CONFIG_NUM = '--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789'
TESSERACT_CONFIG_CHAR = '--psm 11 --oem 3 -c tessedit_char_whitelist=QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm '
URL = "https://teamwood.itch.io/super-auto-pets"

class ActionTypes(enum.Enum):
    """Action types for the game"""
    SET = 1
    SELL = 2
    FREEZE = 3
    ROLL = 4
    END = 5

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

    EMPTY_SLOTS: list[Image]

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
            availableShopSlots = self.GetAllAvailableShopSlots()
            
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

            # Check if Start Slot is Empty
            if(self.IsSlotEmpty(startSlot)):
                return False

        elif(action == ActionTypes.SELL):
            # Check if the slot is a shop slot
            if(startSlot >= 5):
                return False
            
            # Check if the slot is empty
            if(self.IsSlotEmpty(startSlot)):
                return False

        elif(action == ActionTypes.FREEZE):
            # Check if the slot is an animal slot
            if(startSlot < 5):
                return False

            # Check if the slot is empty
            if(self.IsSlotEmpty(startSlot)):
                return False

        return True
    
    def GetNumberOfShopSlots(self) -> int:
        noOfSlots = 0

        if(round >= 1):
            noOfSlots += 3
        
        if(round >= 5):
            noOfSlots += 1

        if(round >= 9):
            noOfSlots += 1

        return noOfSlots

    def GetNumberOfFoodSlots(self) -> int:
        noOfSlots = 0

        if(round >= 1):
            noOfSlots += 1

        if(round >= 3):
            noOfSlots += 1

        return noOfSlots

    def GetAllAvailableShopSlots(self) -> list[bool]:
        availableSlots = [False] * 7
        noOfSlots = self.GetNumberOfShopSlots()

        for i in range(noOfSlots):
            availableSlots[i] = True

        noOfSlots = self.GetNumberOfFoodSlots()

        for i in range(5, 5 + noOfSlots):
            availableSlots[i] = True

        return availableSlots

    def GetSlots(self) -> list[Image]:
        slots = []
        slots.extend(self.animalSlots)
        slots.extend(self.shopSlots)    
        slots.extend(self.foodSlots)
        return slots

    def IsSlotEmpty(self, slot: int) -> bool:
        res = cv2.matchTemplate(self.EMPTY_SLOTS[slot], self.GetSlots()[slot], cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= 0.99)

        if(len(loc) == 0):
            return False

        return True

    def __str__(self) -> str:
        return f"Gold: {self.gold}, Lives: {self.lives}, Round: {self.round}, Cost: {self.cost}"
    
    def DumpStateImages(self):
        for i ,img in enumerate(self.GetSlots()):
            img.save(f"slot{i}.png")
    
class SAP_API:
    state: GameState
    sap : WebElement
    window: str
    driver: webdriver.Chrome
    wait : WebDriverWait
    SLOT_LOCATIONS : list[tuple[int, int]]
    close : np.ndarray

    def __init__(self, driver: webdriver.Chrome, window: str):
        self.close = np.array(PILImage.open("close.png"))

        self.driver = driver
        self.window = window
        self.wait = WebDriverWait(self.driver, 60)

        self.driver.get(URL)

        self.CreateSlotLocs()

        # Get the Run Game Option
        runGameButton : WebElement = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, RUN_GAME_CLASS_NAME ))) 
        runGameButton.click()

        # Get the SAP Window
        self.sap : WebElement = self.wait.until(EC.presence_of_element_located((By.ID, GAME_ID)))
        
    def __del__(self):
        self.driver.switch_to.window(self.window)
        self.driver.close()

    async def CreateSlotLocs(self):
        # Animal Slots
        for i in range(5):
            self.SLOT_LOCATIONS.append((ANIMAL_SLOTS_START[0] + i * ANIMAL_SLOTS_SIZE[0], ANIMAL_SLOTS_START[1] + i * ANIMAL_SLOTS_SIZE[1]))

        # Animal Shop
        for i in range(5):
            self.SLOT_LOCATIONS.append((SHOP_SLOTS_START[0] + i * SHOP_SLOTS_SIZE[0], SHOP_SLOTS_START[1] + i * SHOP_SLOTS_SIZE[1]))

        # Food Shop
        for i in range(2):
            self.SLOT_LOCATIONS.append((FOOD_SLOTS_START[0] + i * SHOP_SLOTS_SIZE[0], FOOD_SLOTS_START[1] + i * SHOP_SLOTS_SIZE[1]))

    def InitializeGame(self):
        # Get the game to the menu
        self.GetToMenu()
        # Initialize Settings
        self.PerformClicks(SETTINGS)

        self.PerformClick((0 , 0))

        capture = self.GetCapture()
        px = (0, 0, 0)

        # Check if in the game
        while(px != (95, 201, 247, 255)):
            capture = self.GetCapture()
            px = capture.getpixel((0, 0))
            sleep(1)

        self.CloseHints()

    def GetCapture(self) -> Image:  
        # Get the game capture
        return PILImage.open(io.BytesIO(self.sap.screenshot_as_png))

    def IsFinishedDownloading(self) -> bool:
        # Check if the game is finished downloading
        img = self.GetCapture()

        # When Loading Background is Black
        px = img.getpixel((0, 0))
        if(px[0] < 20 and px[1] < 20 and px[2] < 20):
            return False
        
        return True

    def GetToMenu(self) -> None:
        """Will get the game to the menu."""

        capture = self.GetCapture()

        # Check if EULA is UP
        while(not self.CanFindString(capture, "consent")):
            self.sap.click()
            capture = self.GetCapture()
            sleep(10)
        
        # Accept EULA
        loc = self.FindLocationOfString(capture, "Accept")
        self.PerformClick(loc)

        # Check if Login screen is up
        while(not self.CanFindString(capture, "Guest", TESSERACT_CONFIG_CHAR)):
            capture = self.GetCapture()
            sleep(1)
        
        # Login as Guest
        self.PerformClick(self.FindLocationOfString(capture, "Guest", TESSERACT_CONFIG_CHAR))

        # Check if News is up
        while(not self.CanFindString(self.PreprocessForOCR(capture), "News", TESSERACT_CONFIG_CHAR)):
            capture = self.GetCapture()
            sleep(1)

        # Dismiss News
        self.PerformClick((-500, 50))
    
    def CloseHints(self):
        # Close Hints found in the game
        while(True):
            res = cv2.matchTemplate(self.close, np.array(self.GetCapture()), cv2.TM_CCOEFF_NORMED)
            loc = np.where(res >= 0.9)

            if(len(loc) == 0):
                break

            self.PerformClick((loc[0] + self.close.size[0], loc[1] + self.close.size[1]))
            sleep(2)

    def GetGameState(self) -> GameState:
        for _ in range(5):
            self.performClick((0, 0))
            sleep(0.1)

        self.CloseHints()

        for _ in range(3):
            self.performClick((0, 0))
            sleep(0.1)

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
        self.state = GameState()
        self.state.fullGame = capture

        # Use OCR
        self.state.gold = self.ConvertToInt(gold, True)
        self.state.lives = self.ConvertToInt(lives)
        self.state.round = self.ConvertToInt(rounds)
        self.state.cost = self.ConvertToInt(costs)

        # Get the slots
        self.state.animalSlots = self.GetSlots(capture, ANIMAL_SLOTS_START, ANIMAL_SLOTS_SIZE, 5)
        self.state.shopSlots = self.GetSlots(capture, SHOP_SLOTS_START, SHOP_SLOTS_SIZE, self.state.GetNumberOfShopSlots())
        self.state.foodSlots = self.GetSlots(capture, FOOD_SLOTS_START, SHOP_SLOTS_SIZE, self.state.GetNumberOfFoodSlots())

        return self.state

    def PerformClick(self, coord : tuple[int, int]):
        ActionChains(self.driver).move_to_element_with_offset(self.sap, coord[0], coord[1]).click().perform()

    def PerformClicks(self, coords : list[tuple[int, int]]):
        act = ActionChains(self.driver)
        for coord in coords:
            act.move_to_element_with_offset(self.sap, coord[0], coord[1]).click()
            act.pause(0.1)
        act.perform()

    def Set(self, startSlot : int, endSlot : int):
        self.PerformClick(self.SLOT_LOCATIONS[startSlot])
        self.PerformClick(self.SLOT_LOCATIONS[endSlot])

    def Sell(self, slot : int):
        self.PerformClick(self.SLOT_LOCATIONS[slot])
        self.PerformClick(FREEZE_SELL_BUTTON)

    def Freeze(self, slot : int):
        self.PerformClick(self.SLOT_LOCATIONS[slot])
        self.PerformClick(FREEZE_SELL_BUTTON)

    def Roll(self):
        self.PerformClick(ROLL_BUTTON)
    
    def EndRound(self):
        self.PerformClick(END_ROUND_BUTTON)

    def PerformAction(self, action: ActionTypes, startSlot: int, endSlot: int) -> bool:
        if(not self.state.IsActionValid(action, startSlot, endSlot)):
            return False

        if(action == ActionTypes.SET):
            self.Set(startSlot, endSlot)
        elif(action == ActionTypes.SELL):
            self.Sell(startSlot)
        elif(action == ActionTypes.FREEZE):
            self.Freeze(startSlot)
        elif(action == ActionTypes.ROLL):
            self.Roll()
        elif(action == ActionTypes.END):
            self.EndRound()

        return True

    @staticmethod
    def CanFindString(capture: Image, find : str, config = "") -> bool:
        # Check if the String can be found
        capStr : str = pyt.image_to_string(capture, config = config)
        capStr = capStr.lower()
        if(capStr.find(find.lower()) != -1):
            return True
        
        return False

    @staticmethod
    def FindLocationOfString(capture : Image, find : str, config = "") -> tuple[int,int]:
        boxes : list[str] = pyt.image_to_boxes(capture, config = config).split("\n")
        
        # Make String from Boxes
        string = ""
        for box in boxes:    
            string += box.split(" ")[0]

        # Find Index of string to find
        string = string.lower()
        idx = string.find(find.lower())

        # Cannot Find String
        if(idx == -1):
            return None

        # return the box location
        x, y = tuple(boxes[idx].split(" ")[3:5])
        return (int(x) - (WIDTH // 2), (HEIGHT // 2) - int(y))

    @staticmethod
    def PreprocessForOCR(img: Image):
        img = img.convert("L")
        img = img.point(lambda p: 255 if p < 128 else 0)
        img = cv2.floodFill(np.array(img), None, (0,0), 255)
        img = PILImage.fromarray(img[1])
        return img

    @staticmethod
    def ConvertToInt(img: Image, ignoreErrors = False):
        temp = pyt.image_to_string(img, config=TESSERACT_CONFIG_NUM)
        if(temp != ""):
            return int(temp)
        elif(ignoreErrors):
            return 0
        else:
            raise Exception("OCR returned nothing")
    
    @staticmethod
    def GetSlots(img: Image, start : tuple[int, int], size: tuple[int, int], noOfSlots ) -> list[Image]:
        slots = []

        left, top = start
        bottom = top + size[1]
        for i in range(noOfSlots):
            right = left + size[0]

            slot = img.crop((left, top, right, bottom))
            slots.append(slot)
            left = right

        return slots

if __name__ == '__main__':
    options = Options()
    options.add_argument("--mute-audio")
    driver = webdriver.Chrome(service = Service(ChromeDriverManager().install()), options= options)
    driver.maximize_window()

    sap = SAP_API(driver, driver.current_window_handle)
    sap.InitializeGame()

    print("Game Initialized")