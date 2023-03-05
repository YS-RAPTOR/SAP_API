from SAP_API.API.Constants import *
from SAP_API.API.Options import Options
from SAP_API.Common.UserLogin import UserLogin
from SAP_API.API.StateTypes import StateTypes
from SAP_API.Common.GameSettings import GameSettings
from SAP_API.API.ActionCompletionType import CompletionType

from io import BytesIO
from collections import deque
from time import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.remote.webelement import WebElement
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image
import pytesseract as pyt

class SAP:
    def __init__(self, options : Options, gameSettings: GameSettings, userLogin: UserLogin) -> None:

        # API Options
        self.options = options
        self.gameSettings = gameSettings
        self.userLogin = userLogin

        # Selenium
        driverOptions = Options()
        driverOptions.add_argument("--mute-audio")
        self.driver : webdriver.Chrome = webdriver.Chrome(service = Service(ChromeDriverManager().install()), options= driverOptions)
        self.driver.maximize_window()
        self.driver.get(URL)
        self.sap : WebElement = None

        self.isInitialized = False

        # Tasks
        import SAP_API.API.Actions as Actions

        self.taskList: deque[Actions.Action] = deque()
        self.CompletionType : CompletionType = CompletionType.NEXT_STATE
        self.taskList.extend([Actions.InitializeGameWindow()])
        self.taskStartTime = 0
        self.taskRunning = False
        self.taskTries = 0
        self.taskCompletion = False

        # Task Completion
        self.FrameCache : deque[Image.Image] = deque(maxlen=self.options.NoOfEqualFramesBeforeCompletion)
        self.StartFrame : Image.Image = None

    def AddTask(self, task: StateTypes) -> None:
        """#TODO IMPLEMENT"""

    def Ready(self) -> bool:
        return len(self.taskList) == 0
    
    def SetTaskCompletion(self, completionType: CompletionType) -> None:
        self.CompletionType = completionType
    
    def IsInState(self, state: StateTypes) -> bool:
        match state:
            case StateTypes.NOT_INITIALIZED:
                # Check if the run game button is visible
                return self.isInitialized
            case StateTypes.PRIVACY_POLICY:
                # Check if the privacy policy button is visible
                return self.CanFindString(self.FrameCache[-1], "consent")

    def PreStart(self):
        if(self.isInitialized):
            self.GetCapture()
            self.StartFrame = self.FrameCache[0].copy()
        
        self.taskRunning = True
        self.taskStartTime = time()
        self.taskTries += 1

    def Tick(self) -> bool:
        # Is the task list empty?
        if(self.Ready()):
            return

        # If no task is running, then start the next task
        if(not self.taskRunning):
            #TODO Explore Moving it into DoTask
            self.PreStart()
            self.taskList[0].DoTask(self)

        # Check time out
        if(time() - self.taskStartTime > self.options.taskTimeout and not self.taskList[0].ignoreTimeout):
            # Check how many times the task has been tried
            if(self.taskTries > self.options.timeoutRetry):
                raise Exception("Task timed out")
            
            self.PreStart()
            self.taskList[0].DoTask(self)

        self.GetCapture()

        # Check task completion
        match self.CompletionType:
            case CompletionType.NEXT_STATE:
                self.CheckIfNextState()
            case CompletionType.NO_CHANGES:
                self.CheckIfNoChanges()
            case CompletionType.NO_CHANGES_AND_NOT_INITIAL_STATE:
                self.CheckIfNoChangesAndNotInitialState()

        if(self.taskCompletion):
            self.taskCompletion = False
            self.taskRunning = False
            self.taskList.popleft()
            self.taskTries = 0
            return True
        
        return False
        
    def GetCapture(self) -> None:
        self.FrameCache.append(Image.open(BytesIO(self.sap.screenshot_as_png)))

    def CheckIfNextState(self) -> None:
        for state in self.taskList[0].NextStates:
            if(self.IsInState(state)):
                self.taskCompletion = True
                return True

    def CheckIfNoChanges(self) -> bool:
        """#TODO Implement"""

    def CheckIfNoChangesAndNotInitialState(self) -> bool:
        """#TODO Implement"""


    @staticmethod
    def CanFindString(capture: Image, find : str, config = "") -> bool:
        # Check if the String can be found
        capStr : str = pyt.image_to_string(capture, config = config)
        capStr = capStr.lower()


        if(capStr.find(find.lower()) != -1):
            return True
        
        return False