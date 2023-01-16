import time
import numpy as np
from SAP_API import SAP_API
from ActionTypes import ActionTypes

class Randy:
    def __init__(self):
        self.api = SAP_API()
        self.api.InitializeGame()
        self.logs : list[str] = []
        
    def GetRandomAction(self) -> ActionTypes:
        i = np.random.choice([1,2,3,4,5], p=[0.3, 0.3, 0.3, 0.05, 0.05])
        return ActionTypes(i)


    def run(self):
        while True:
            state = self.api.GetGameState()
            action = self.GetRandomAction()
            start = np.random.randint(1,12)

            if(start >= 5 and start <= 10 and np.random.rand() < 0.20):
                start = np.random.randint(5, 10)

            end = np.random.randint(1,12)

            try:
                status = self.api.PerformAction(action, start, end)
            except Exception as e:
                print(f"Action {action} from {start} to {end} | Status : {status} | Time: {time.time()} | State: {s} \n")
                state.DumpState("log")
                raise e
            
            s = str(state).replace("\n", " ")
            l = f"Action {action} from {start} to {end} | Status : {status} | Time: {time.time()} | State: {s} \n"
            self.logs.append(l)
            if(len(self.logs) > 10):
                with open("logs.txt", "a") as f:
                    for log in self.logs:
                        f.writelines(log)
                self.logs = []


if __name__ == '__main__':
    bot = Randy()
    bot.run()