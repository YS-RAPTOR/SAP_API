from SAP_API.API.SAP import SAP
from SAP_API.API.Options import Options
from SAP_API.Common.UserLogin import UserLogin
from SAP_API.Common.GameSettings import GameSettings

if __name__ == '__main__':
    options = Options()
    gameSettings = GameSettings()
    userLogin = UserLogin()

    api = SAP(options, gameSettings, userLogin)
    while True:
        if(api.Tick()):
            print("Task Completed")