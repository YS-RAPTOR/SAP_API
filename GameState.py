import os
import cv2
import numpy as np
from PIL.Image import Image
import PIL.Image as PILImage
from dataclasses import dataclass

from ActionTypes import ActionTypes

@dataclass
class GameState:
    """Game state"""
    # 5 animal slots, 5 shop slots, 2 food slots
    # Total slots is 12 slots. Store as Array of images
    __EMPTY_SLOTS = []
    __NOT_AVAILABLE = []

    def __init__(self):
        self.fullGame : Image = None

        self.animalSlots : list[Image] = []
        self.shopSlots : list[Image] = []
        self.foodSlots : list[Image] = []
        
        for i in range(12):
            self.__EMPTY_SLOTS.append(np.array(PILImage.open(f"Assets/EmptySlots/slot{i}.png")))

        for i in range(3):
            self.__NOT_AVAILABLE.append(np.array(PILImage.open(f"Assets/NotAvailableSlots/NA{i}.png")))
            pass

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

    def GetAllAvailableShopSlots(self) -> list[bool]:
        availableSlots = [True] * 7
        slots = self.GetSlots()

        for slot in range(3, 6):
            res = cv2.matchTemplate(self.__NOT_AVAILABLE[slot - 3], np.array(slots[slot + 5]), cv2.TM_CCOEFF_NORMED)
            loc = np.where(res >= 0.8)

            if(len(loc[0]) != 0 or len(loc[1]) != 0):
                availableSlots[slot] = False

        return availableSlots

    def GetSlots(self) -> list[Image]:
        slots = []
        slots.extend(self.animalSlots)
        slots.extend(self.shopSlots)
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