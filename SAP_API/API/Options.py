from dataclasses import dataclass

@dataclass
class Options:
    
    def __init__(self, noOfRetries = 3, timeoutRetry = 2, NoOfEqualFramesBeforeCompletion = 5, taskTimeout = 10) -> None:
        self.noOfRetries : int = noOfRetries
        self.timeoutRetry: int = timeoutRetry
        self.NoOfEqualFramesBeforeCompletion: int = NoOfEqualFramesBeforeCompletion
        self.taskTimeout: int = taskTimeout