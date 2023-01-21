import io
import socket
from PIL import Image

from SAP_API.Common.Results import Results
from SAP_API.Common.GameState import GameState
from SAP_API.Common.ActionTypes import ActionTypes
from SAP_API.Common.ClientServer.Messages import MessageTypes, ServerErrors
from SAP_API.Common.ClientServer.Communication import GetMessage, CreateMessage
from SAP_API.Common.ClientServer.Serialization import DeserializeError , SerializeAction, DeserializeActionResponse

class Client:
    def __init__(self, ip : str, port : int):
        self.ip = ip
        self.port = port

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((ip, port))

        self.ReceiveInit()
        self.InitializeGame()

    def __del__(self):
        self.sock.close()

    def HandleErrors(self, msgType : MessageTypes, msg : bytearray) -> bool:
        print(msgType)

        if(msgType == MessageTypes.ERROR_RESPONSE):
            
            error = DeserializeError(msg)
            print(error)
            
            if(error == ServerErrors.TIMEOUT):
                print("Restarting client")
                self.Reset()

            return False

        return True
    
    def Reset(self):
        self.sock.close()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.ip, self.port))
        self.ReceiveInit()
        self.InitializeGame()

    def ReceiveInit(self) -> bool:
        
        msg = GetMessage(self.sock)

        if(msg == None):
            return False

        msgType, msg = msg

        if(not self.HandleErrors(msgType, msg)):
            return False

        if(msgType != MessageTypes.INIT):
            return False

        return True

    def InitializeGame(self) -> bool:
        self.sock.send(CreateMessage(MessageTypes.INITIALIZE_GAME, b'1'))
        
        msg = GetMessage(self.sock)

        if(msg == None):
            return False

        msgType, msg = msg

        if not self.HandleErrors(msgType, msg):
            return False

        if msgType != MessageTypes.INITIALIZE_GAME_RESPONSE:
            return False
        
        return True
    
    def GetGameState(self) -> GameState:
        self.sock.send(CreateMessage(MessageTypes.GET_GAME_STATE, b'1'))
        
        gameState = GameState()
        gameState.animalSlots = [None] * 5
        gameState.shopSlots = [None] * 5
        gameState.foodSlots = [None] * 2

        slotResponses = [MessageTypes(i) for i in range(MessageTypes.GET_GAME_STATE_RESPONSE_SLOT0.value, MessageTypes.GET_GAME_STATE_RESPONSE_SLOT11.value + 1)]
        for i in range(14):
            msg = GetMessage(self.sock)

            if(msg == None):
                return None

            msgType, msg = msg

            if not self.HandleErrors(msgType, msg):
                return None

            if(msgType == MessageTypes.GET_GAME_STATE_RESPONSE_STATE):
                gold, lives, rounds = msg.decode("utf-8").split(",")
                gameState.gold = int(gold)
                gameState.lives = int(lives)
                gameState.round = int(rounds)

            elif(msgType == MessageTypes.GET_GAME_STATE_RESPONSE_FULL_GAME):
                gameState.fullGame = Image.open(io.BytesIO(msg))

            elif(msgType in slotResponses):
                index = msgType.value - MessageTypes.GET_GAME_STATE_RESPONSE_SLOT0.value
                
                if(index < 5):
                    gameState.animalSlots[index] = Image.open(io.BytesIO(msg))
                elif(index < 10):
                    gameState.shopSlots[index - 5] = Image.open(io.BytesIO(msg))
                else:
                    gameState.foodSlots[index - 10] = Image.open(io.BytesIO(msg))
            else:
                return None

        return gameState        

    def PerformAction(self, actionType : ActionTypes, start : int , end : int ) -> tuple[bool, Results]:
        self.sock.send(CreateMessage(MessageTypes.PERFORM_ACTION, SerializeAction(actionType, start, end)))

        msg = GetMessage(self.sock)

        if(msg == None):
            return None

        msgType, msg = msg

        if not self.HandleErrors(msgType, msg):
            return None

        if(msgType != MessageTypes.PERFORM_ACTION_RESPONSE):
            return None

        return DeserializeActionResponse(msg)

    def Debug(self):
        self.sock.send(CreateMessage(MessageTypes.DEBUG, b'1'))

        msg = GetMessage(self.sock)

        if(msg == None):
            return

        msgType, msg = msg

        if not self.HandleErrors(msgType, msg):
            return

        if(msgType != MessageTypes.DEBUG):
            return
