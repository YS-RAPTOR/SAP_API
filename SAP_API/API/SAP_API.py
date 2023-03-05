from SAP_API.API.API_Options import API_Options
from SAP_API.Common.GameSettings import GameSettings
from SAP_API.Common.UserLogin import UserLogin
from SAP_API.API.API_State import API_State
from SAP_API.API.API_Task import API_Task

"""
#  Each State Has to be unique

Completion Requirements for tasks in api:
    1) Check for Next State
    2) Check for No CHanges between Frames

After Performing task Each Tick check for either 1 or 2. Depends on the task I am doing.
Also introduce a timeout for each task. If the task is not completed in the time frame, then it will be considered as failed.
If failed the task will be reattempted. If it fails again, then api will be restarted.

API will be in charge of figuring out the state of the game.
Task will be in charge of doing an action and telling the api task completion criteria.
If can skip task, then task will be skipped if valid starting state is not met.

"""


class SAP_API:
    def __init__(self, options : API_Options, gameSettings: GameSettings, userLogin: UserLogin) -> None:
        self.options = options
        self.gameSettings = gameSettings
        self.userLogin = userLogin

        self.driver = 
    
    def IsInState(self, state: API_State) -> bool:
        match state:
            case API_State.NOT_INITIALIZED:
                pass
    


