from SAP_API.API.SAP_API import SAP_API
from SAP_API.Common.GameState import GameState
from SAP_API.Common.ActionTypes import ActionTypes

class UserBot:
    def __init__(self):
        self.sap = SAP_API()
        self.sap.InitializeGame()

    def run(self):
        while True:
            state = self.sap.GetGameState()
            print(state)
            action = input("Enter Action (S - Set, L - Sell, F - Freeze, R - Roll, E - End, Q - Quit): ")
        
            if(action == "S"):
                start = int(input("Enter Start Slot: "))
                end = int(input("Enter End Slot: "))
                status = self.sap.PerformAction(ActionTypes.SET, start, end)
            elif(action == "L"):
                slot = int(input("Enter Slot: "))
                status = self.sap.PerformAction(ActionTypes.SELL, slot, 0)
            elif(action == "F"):
                slot = int(input("Enter Slot: "))
                status = self.sap.PerformAction(ActionTypes.FREEZE, slot, 0)
            elif(action == "R"):
                status = self.sap.PerformAction(ActionTypes.ROLL, 0, 0)
            elif(action == "E"):
                status = self.sap.PerformAction(ActionTypes.END, 0, 0)
            elif(action == "Q"):
                self.sap.__del__()
                break

            if(not status):
                print("Invalid Action")

if __name__ == '__main__':
    bot = UserBot()
    bot.run()