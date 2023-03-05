from dataclasses import dataclass

@dataclass
class API_Options:
    
    def __init__(self, noOfRetries = 3, NoOfEqualFramesBeforeCompletion = 5) -> None:
        self.noOfRetries = noOfRetries
        self.NoOfEqualFramesBeforeCompletion = NoOfEqualFramesBeforeCompletion