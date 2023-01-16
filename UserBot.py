from SAP_API import SAP_API
from GameState import GameState
from ActionTypes import ActionTypes

if __name__ == '__main__':
    sap = SAP_API()

    sap.InitializeGame()

    while True:

        state = sap.GetGameState()
        print(state)
        print(state.GetAllAvailableShopSlots())
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