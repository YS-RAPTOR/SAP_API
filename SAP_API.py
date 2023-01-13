import enum
import cv2
import io
import cv2  
import os
import numpy as np
import pytesseract as pyt
import PIL.Image as PILImage

import time
from time import sleep
from typing import Self
from PIL.Image import Image
from dataclasses import dataclass

from selenium import webdriver
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
ACTION_DELAY = 10
GOLD_PIXEL_COLOR = (255, 171, 50, 255)

# Crop coordinates
GOLD_CROP = (56,21,107,60)
LIVES_CROP = (168,21,212,60)
ROUNDS_CROP = (424,21,492,60)

GOLD_PIXEL = (30, 40)

RESULTS_CROP = (0, 450, WIDTH, 520)
PLAY_PAUSE_CROP = (460, 0, 575, 50)

ANIMAL_SLOTS_START = (300, 130)
ANIMAL_SLOTS_SIZE = (96, 225)

SHOP_SLOTS_START = (303, 380)
SHOP_SLOTS_SIZE = (96, 170)

FOOD_SLOTS_START = (783, 380)

# Click Locations

END_ROUND_BUTTON = (600, 300)
ROLL_BUTTON = (-600, 300)
FREEZE_SELL_BUTTON = (100, 300)

LATER_BUTTON = (-100, 300)

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

ROUND_SETTINGS = [(0, -300), (100, -300)]

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
class GameState:
    """Game state"""
    # 5 animal slots, 5 shop slots, 2 food slots
    # Total slots is 12 slots. Store as Array of images
    __EMPTY_SLOTS = []

    def __init__(self):
        self.fullGame : Image = None

        self.animalSlots : list[Image] = []
        self.shopSlots : list[Image] = []
        self.foodSlots : list[Image] = []
        
        for i in range(12):
            self.__EMPTY_SLOTS.append(np.array(PILImage.open(f"Assets/EmptySlots/slot{i}.png")))

        self.gold = 0
        self.lives = 0
        self.round = 0

    def __eq__(self, __o: object) -> bool:

        if(isinstance(__o, GameState) == False or __o == None):
            return False

        if(self.gold != __o.gold or self.lives != __o.lives or self.round != __o.round):
            return False

        # Check if the slots are the same
        slots = self.GetSlots()
        otherSlots = __o.GetSlots()

        if(len(slots) != len(otherSlots)):
            return False

        for slot in range(len(slots)):

            if(slots[slot] == None and otherSlots[slot] == None):
                # If both is none then continue
                continue
            elif(slots[slot] == None or otherSlots[slot] == None):
                # If one is none but the other is not then return false
                return False

            res = cv2.matchTemplate(np.array(slots[slot]), np.array(otherSlots[slot]), cv2.TM_CCOEFF_NORMED)
            loc = np.where(res >= 0.99)

            if(len(loc[0]) == 0 or len(loc[1]) == 0):
                return False

        return True

    def __str__(self) -> str:
        return f"Gold: {self.gold}\nLives: {self.lives}\nRound: {self.round}"

    def copy(self) -> Self:
        c = GameState()

        c.fullGame = self.fullGame.copy()
        c.animalSlots = self.animalSlots.copy()
        c.shopSlots = self.shopSlots.copy()
        c.foodSlots = self.foodSlots.copy()

        c.gold = self.gold
        c.lives = self.lives
        c.round = self.round

    def IsActionValid(self, action: ActionTypes, startSlot: int, endSlot: int) -> bool:
        if(action == ActionTypes.SET):
            # Check if the start slot is the same as the end slot
            if(startSlot == endSlot):
                return False

            # Check if the start slot is a shop slot
            if(startSlot >= 5):
                # Check if the shop slot is available
                if(not self.GetAllAvailableShopSlots()[startSlot - 5]):
                    return False

            # Check if the end slot is a shop slot
            if(endSlot >= 5):
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

            # Check if the Shop Slot is available
            if(not self.GetAllAvailableShopSlots()[startSlot - 5]):
                return False

            # Check if the slot is empty
            if(self.IsSlotEmpty(startSlot)):
                return False
                
        elif(action == ActionTypes.ROLL):
            # No Gold to reroll
            if(self.gold == 0):
                return False

        return True
    
    def GetNumberOfShopSlots(self) -> int:
        noOfSlots = 0

        if(self.round >= 1):
            noOfSlots += 3
        
        if(self.round >= 5):
            noOfSlots += 1

        if(self.round >= 9):
            noOfSlots += 1

        return noOfSlots

    def GetNumberOfFoodSlots(self) -> int:
        noOfSlots = 0

        if(self.round >= 1):
            noOfSlots += 1

        if(self.round >= 3):
            noOfSlots += 1

        return noOfSlots

    def GetAllAvailableShopSlots(self) -> list[bool]:
        availableSlots = [False] * 7
        noOfSlots = self.GetNumberOfShopSlots()

        for i in range(noOfSlots):
            availableSlots[i] = True

        noOfSlots = self.GetNumberOfFoodSlots()

        for i in range(6, 6 - noOfSlots, -1):
            availableSlots[i] = True

        return availableSlots

    def GetSlots(self) -> list[Image]:
        slots = []
        slots.extend(self.animalSlots)
        slots.extend(self.shopSlots)
        slots.extend([None] * ((5 - self.GetNumberOfShopSlots()) + (2 - self.GetNumberOfFoodSlots())))    
        slots.extend(self.foodSlots)

        return slots

    def IsSlotEmpty(self, slot: int) -> bool:
        res = cv2.matchTemplate(self.__EMPTY_SLOTS[slot], np.array(self.GetSlots()[slot]), cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= 0.85)

        if(len(loc[0]) == 0 or len(loc[1]) == 0):
            return False

        return True
    
    def DumpState(self, directory = ""):   
        
        if(directory != ""):
            directory += "/"

        if(not os.path.exists(directory) and not directory == ""):
            os.makedirs(directory)

        # txt File with information
        with open(f"{directory}state.txt", "w") as f:
            f.write(str(self))

        # Images of the slots
        self.fullGame.save(f"{directory}fullGame.png")

        for i, animal in enumerate(self.animalSlots):
            animal.save(f"{directory}animal{i}.png")

        for i, shop in enumerate(self.shopSlots):
            shop.save(f"{directory}shop{i}.png")

        for i, food in enumerate(self.foodSlots):
            food.save(f"{directory}food{i}.png")
    
class SAP_API:
    __SLOT_LOCATIONS : list[tuple[int, int]] = []
    __close : np.ndarray = None

    def __init__(self):
        # Setup Static Variables
        if(self.__close == None):
            self.__close = np.array(PILImage.open("Assets/close.png"))

        if(len(self.__SLOT_LOCATIONS) == 0):
            self.__CreateSlotLocs()
        
        # Initialize Variables
        self.__isInitialized = False
        self.__state = None
        self.__prevState = None

        options = Options()
        options.add_argument("--mute-audio")
        self.__driver : webdriver.Chrome = webdriver.Chrome(service = Service(ChromeDriverManager().install()), options= options)
        self.__driver.maximize_window()
        wait = WebDriverWait(self.__driver, 60)
        self.__driver.get(URL)

        # Get the Run Game Option
        runGameButton : WebElement = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, RUN_GAME_CLASS_NAME ))) 
        runGameButton.click()

        # Get the SAP Window
        self.__sap : WebElement = wait.until(EC.presence_of_element_located((By.ID, GAME_ID)))
        
    def __del__(self):
        self.__driver.quit()

    def __CreateSlotLocs(self):
        # Animal Slots
        for i in range(5):
            i += 0.5
            x = (ANIMAL_SLOTS_START[0] + i * ANIMAL_SLOTS_SIZE[0]) - (WIDTH // 2) 
            y = (ANIMAL_SLOTS_START[1] + ANIMAL_SLOTS_SIZE[1] // 2) - (HEIGHT // 2)
            self.__SLOT_LOCATIONS.append((x, y))

        # Animal Shop
        for i in range(5):
            i += 0.5
            x = (SHOP_SLOTS_START[0] + i * SHOP_SLOTS_SIZE[0]) - (WIDTH // 2)
            y = (SHOP_SLOTS_START[1] + SHOP_SLOTS_SIZE[1] // 2) - (HEIGHT // 2)
            self.__SLOT_LOCATIONS.append((x, y))


        # Food Shop
        for i in range(2):
            i += 0.5
            x = (FOOD_SLOTS_START[0] + i * SHOP_SLOTS_SIZE[0]) - (WIDTH // 2)
            y = (FOOD_SLOTS_START[1] + SHOP_SLOTS_SIZE[1] // 2) - (HEIGHT // 2)
            self.__SLOT_LOCATIONS.append((x, y))

    def InitializeGame(self):
        # Get the game to the menu
        self.__GetToMenu()
        # Initialize Settings
        self.__PerformClicks(SETTINGS)

        self.__MenuToGame()

        self.__CloseHints()

    def __GetCapture(self) -> Image:  
        # Get the game capture
        return PILImage.open(io.BytesIO(self.__sap.screenshot_as_png))

    def __GetToMenu(self) -> None:
        """Will get the game to the menu."""

        capture = self.__GetCapture()

        # Check if EULA is UP
        while(not self.CanFindString(capture, "consent")):
            self.__sap.click()
            capture = self.__GetCapture()
            sleep(10)
        
        # Accept EULA
        loc = self.FindLocationOfString(capture, "Accept")
        self.__PerformClick(loc)

        # Check if Login screen is up
        while(not self.CanFindString(capture, "Guest", TESSERACT_CONFIG_CHAR)):
            capture = self.__GetCapture()
            sleep(1)
        
        # Login as Guest
        self.__PerformClick(self.FindLocationOfString(capture, "Guest", TESSERACT_CONFIG_CHAR))

        # Check if News is up
        while(not self.CanFindString(self.PreprocessForOCR(capture), "News", TESSERACT_CONFIG_CHAR)):
            capture = self.__GetCapture()
            sleep(1)

        # Dismiss News
        self.__PerformClick((-500, 50))
    
    def __MenuToGame(self):
        self.__PerformClick((0 , 0))

        # Check if in the game
        while(not self.__IsInGame()):
            sleep(1)

    def __IsInGame(self) -> bool:
        capture = self.__GetCapture()
        px = capture.getpixel(GOLD_PIXEL)
        return px == GOLD_PIXEL_COLOR

    def __CloseHints(self):
        # Close Hints found in the game
        while(True):
            res = cv2.matchTemplate(self.__close, np.array(self.__GetCapture()), cv2.TM_CCOEFF_NORMED)
            loc = np.where(res >= 0.9)

            if(len(loc[0]) == 0 or len(loc[1]) == 0):
                break

            self.__PerformClick(((loc[1][0] + 2) - (WIDTH//2), (loc[0][0] + 2) - (HEIGHT // 2)))
            sleep(2)

    def GetGameState(self) -> GameState:
        self.__PerformClicks([(0,0)] * 5, 0.25)
        self.__CloseHints()
        self.__PerformClicks([(0,0)] * 3, 0.25)

        # Capture the game
        capture = self.__GetCapture()
        
        # Crop the game characters for OCR
        gold = capture.crop(GOLD_CROP)
        lives = capture.crop(LIVES_CROP)
        rounds = capture.crop(ROUNDS_CROP)
        # costs = capture.crop(COST_CROP)

        # Preprocess the images for OCR
        gold = self.PreprocessForOCR(gold)
        lives = self.PreprocessForOCR(lives)
        rounds = self.PreprocessForOCR(rounds)

        self.__state = GameState()

        # Setup Game State
        self.__state.fullGame = capture

        # Use OCR
        self.__state.gold = self.ConvertToInt(gold, True)
        self.__state.lives = self.ConvertToInt(lives)
        self.__state.round = self.ConvertToInt(rounds)

        # Get the slots
        self.__state.animalSlots = self.GetSlots(capture, ANIMAL_SLOTS_START, ANIMAL_SLOTS_SIZE, 5)
        self.__state.shopSlots = self.GetSlots(capture, SHOP_SLOTS_START, SHOP_SLOTS_SIZE, self.__state.GetNumberOfShopSlots())
        self.__state.foodSlots = self.GetSlots(capture, FOOD_SLOTS_START, SHOP_SLOTS_SIZE, self.__state.GetNumberOfFoodSlots(), True)

        return self.__state

    def __PerformClick(self, coord : tuple[int, int]):
        ActionChains(self.__driver).move_to_element_with_offset(self.__sap, coord[0], coord[1]).click().perform()

    def __PerformClicks(self, coords : list[tuple[int, int]], delay = 0.1):
        act = ActionChains(self.__driver)
        for coord in coords:
            act.move_to_element_with_offset(self.__sap, coord[0], coord[1]).click()
            act.pause(delay)
        act.perform()

    def __Set(self, startSlot : int, endSlot : int):
        self.__PerformClicks([self.__SLOT_LOCATIONS[startSlot], self.__SLOT_LOCATIONS[endSlot]], 1)

    def __Sell(self, slot : int):
        self.__PerformClicks([self.__SLOT_LOCATIONS[slot], FREEZE_SELL_BUTTON], 1)

    def __Freeze(self, slot : int):
        self.__PerformClicks([self.__SLOT_LOCATIONS[slot], FREEZE_SELL_BUTTON], 1)

    def __Roll(self):
        self.__PerformClick(ROLL_BUTTON)
    
    def __EndRound(self):
        self.__PerformClick(END_ROUND_BUTTON)
        
        skip = False
        # Check if Match Screen is up
        while(not self.CanFindString(self.__GetCapture().crop(PLAY_PAUSE_CROP), "P", TESSERACT_CONFIG_CHAR)):
            # If you see results screen, skip initialization for this round.
            if self.__GetResult():
                skip = True
                break

        # Setup AutoPlay and Fast Forward
        if(not self.__isInitialized and not skip):
            self.__PerformClicks(ROUND_SETTINGS)
            self.__isInitialized = True

        # Get Outcomes for the Round
        while not self.__GetResult():
            sleep(1)

        self.BringBackToGame()

    def __GetResult(self) -> bool:
        capture = self.__GetCapture().crop(RESULTS_CROP)
        capStr : str = pyt.image_to_string(capture, config = TESSERACT_CONFIG_CHAR)
        capStr = capStr.lower()

        if(capStr.find("defeat") != -1):
            self.result = Results.LOSE
            return True
        elif(capStr.find("victory") != -1):
            self.result = Results.WIN
            return True
        elif(capStr.find("draw") != -1):
            self.result = Results.DRAW
            return True
        elif(capStr.find("gamewon") != -1):
            self.result = Results.WIN
            return True
        elif(capStr.find("gameover") != -1):
            self.result = Results.LOSE
            return True
        else:
            return False

    def BringBackToGame(self):
        capture = self.__GetCapture()
        while True:
            if(capture.getpixel(GOLD_PIXEL) == GOLD_PIXEL_COLOR):
                return
            elif(self.CanFindString(capture, "Guest"), TESSERACT_CONFIG_CHAR):
                self.__PerformClick(LATER_BUTTON)

            self.__PerformClick((0, 0))
            capture = self.__GetCapture()
            sleep(1)

    def PerformAction(self, action: ActionTypes, startSlot: int, endSlot: int) -> bool:
        for _ in range(2):

            if(not self.__state.IsActionValid(action, startSlot, endSlot)):
                return False

            if(action == ActionTypes.SET):
                self.__Set(startSlot, endSlot)
            elif(action == ActionTypes.SELL):
                self.__Sell(startSlot)
            elif(action == ActionTypes.FREEZE):
                self.__Freeze(startSlot)
            elif(action == ActionTypes.ROLL):
                self.__Roll()
            elif(action == ActionTypes.END):
                self.__EndRound()


            sleep(ACTION_DELAY)
            
            # Check if there is a difference in the game state
            self.__prevState = self.__state
            self.GetGameState()

            if(self.__prevState == self.__state):
                # ! This Dump is For Debugging
                # * This Dump is For Debugging
                directory = f"Errors/{action} {startSlot} {endSlot} - {time.time()}"
                print(directory)
                self.__prevState.DumpState(directory + "/Prev")
                self.__state.DumpState(directory + "/Curr")
                continue

            return True

        return False

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
    def PreprocessForOCR(img: Image, threshold = 180):
        img = img.convert("L")
        img = img.point(lambda p: 255 if p < threshold else 0)
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
    def GetSlots(img: Image, start : tuple[int, int], size: tuple[int, int], noOfSlots, isFoodSlots = False ) -> list[Image]:
        slots = []

        if isFoodSlots:
            right, top = (start[0] + size[0] * 2, start[1])
            bottom = top + size[1]

            for _ in range(noOfSlots):
                left = right - size[0]

                slot = img.crop((left, top, right, bottom))
                slots.append(slot)
                right = left

            return slots

        left, top = start
        bottom = top + size[1]
        for _ in range(noOfSlots):
            right = left + size[0]

            slot = img.crop((left, top, right, bottom))
            slots.append(slot)
            left = right

        return slots

if __name__ == '__main__':
    sap = SAP_API()

    sap.InitializeGame()

    while True:

        state = sap.GetGameState()
        print(state)

        action = input("Enter Action (S - Set, L - Sell, F - Freeze, R - Roll, E - End, Q - Quit): ")
    
        if(action == "S"):
            start = int(input("Enter Start Slot: "))
            end = int(input("Enter End Slot: "))
            status = sap.PerformAction(ActionTypes.SET, start, end)
        elif(action == "L"):
            slot = int(input("Enter Slot: "))
            status = sap.PerformAction(ActionTypes.SELL, slot, 0)
        elif(action == "F"):
            slot = int(input("Enter Slot: "))
            status = sap.PerformAction(ActionTypes.FREEZE, slot, 0)
        elif(action == "R"):
            status = sap.PerformAction(ActionTypes.ROLL, 0, 0)
        elif(action == "E"):
            status = sap.PerformAction(ActionTypes.END, 0, 0)
        elif(action == "Q"):
            sap.__del__()
            break

        if(not status):
            print("Invalid Action")