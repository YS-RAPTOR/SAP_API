import SAP_API.API.SAP as SAP
from SAP_API.API.StateTypes import StateTypes
from SAP_API.API.ActionCompletionType import CompletionType
from SAP_API.API.Constants import RUN_GAME_CLASS_NAME, GAME_ID

from abc import ABC, abstractmethod

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC

class Action(ABC):
    def __init__(self, canSkip : bool, completionType:CompletionType, ignoreTimeout = False ) -> None:
        self.canSkip = canSkip
        self.completionType = completionType
        self.ignoreTimeout = ignoreTimeout
        self.validStartingStates : list[StateTypes] = []
        self.NextStates: list[StateTypes] = []

    def IsValidStartingState(self, api : SAP.SAP) -> bool:
        for state in self.validStartingStates:
            if(api.IsInState(state)):
                return True
        
        return False

    @abstractmethod
    def DoTask(self, api: SAP.SAP) -> bool:
        api.SetTaskCompletion(self.completionType)
        if(self.canSkip and not self.IsValidStartingState(api)):
            return True

class InitializeGameWindow(Action):
    def __init__(self) -> None:
        super().__init__(False, CompletionType.NEXT_STATE, True)
        self.validStartingStates = [StateTypes.NOT_INITIALIZED]
        self.NextStates = [StateTypes.PRIVACY_POLICY]

    def DoTask(self, api : SAP.SAP) -> bool:
        super().DoTask(api)
        
        wait = WebDriverWait(api.driver, 60)

        # Get the Run Game Option
        runGameButton : WebElement = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, RUN_GAME_CLASS_NAME ))) 
        runGameButton.click()

        # Get the SAP Window
        api.sap : WebElement = wait.until(EC.presence_of_element_located((By.ID, GAME_ID)))
        api.isInitialized = True



