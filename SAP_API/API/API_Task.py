from SAP_API.API.SAP_API import SAP_API

from abc import ABC, abstractmethod
from enum import Enum, auto

class TaskCompletionType (Enum):
    NEXT_STATE = auto()
    NO_CHANGES = auto()
    NO_CHANGES_AND_NOT_INITIAL_STATE = auto()

class API_Task(ABC):
    def __init__(self, canSkip : bool, completionType: TaskCompletionType ) -> None:
        self.canSkip = canSkip
        self.completionType = completionType
        self.validStartingStates = []

    def IsValidStartingState(self, api: SAP_API) -> bool:
        for state in self.validStartingStates:
            if(api.IsInState(state)):
                return True
        
        return False

    @abstractmethod
    def DoTask(self, api: SAP_API) -> bool:
        api.SetTaskCompletion(self.completionType)
        if(self.canSkip and not self.IsValidStartingState(api)):
            return True

class InitializeGameWindow(API_Task):
    def __init__(self) -> None:
        super().__init__(False, TaskCompletionType.NEXT_STATE)


    def DoTask(self, api: SAP_API) -> bool:
        super().DoTask(api)




