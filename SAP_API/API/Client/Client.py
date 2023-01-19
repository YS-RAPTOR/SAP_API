import socket
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

        msg = GetMessage(self.sock)

        if(msg == None):
            return None

        msgType, msg = msg

        if not self.HandleErrors(msgType, msg):
            return None

        if(msgType != MessageTypes.GET_GAME_STATE_RESPONSE):
            return None

        return GameState(msg)

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

    def DEBUG(self):
        self.sock.send(CreateMessage(MessageTypes.DEBUG, b'1'))

        msg = GetMessage(self.sock)

        if(msg == None):
            return

        msgType, msg = msg

        if not self.HandleErrors(msgType, msg):
            return

        if(msgType != MessageTypes.DEBUG):
            return
