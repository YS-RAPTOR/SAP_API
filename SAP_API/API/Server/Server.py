import os
import time
import signal
import socket
import select
import platform
from multiprocessing import Process, Value, Array, Queue, RLock

from SAP_API.API.SAP_API import SAP_API
from SAP_API.Common.ClientServer.Constants import *
from SAP_API.Common.ClientServer.Messages import MessageTypes, ServerErrors
from SAP_API.Common.ClientServer.Communication import GetMessage, CreateMessage
from SAP_API.Common.ClientServer.Serialization import DeserializeAction, SerializeActionResponse, SerializeError

class Main2ProcessSharedVals:
    def __init__(self):
        self.lock = RLock()

        self.RequestType = Value("i", -1)
        self.RequestData = Array("c", 32)
        self.TimeoutTime = Value("d", 0)

        self.driverPID = Value("i", -1)

class Server:
    def __init__(self, host : str, port : int, whitelist : list[str], maxClients : int, timeoutTime : int, debug : bool = False,  ):
        self.whitelist = whitelist
        self.debug = debug
        self.maxClients = maxClients
        self.timeoutTime = timeoutTime * 60
        
        self.sockets : list[socket.socket] = [socket.socket(socket.AF_INET, socket.SOCK_STREAM)]
        self.sockets[0].bind((host, port))

        self.clientsProcesses : dict[int, tuple[Process, APIProcess]] = {}
        self.shared : dict[int, Main2ProcessSharedVals] = {}
        # 16 is the max responses a single request can have
        self.responses = Queue(self.maxClients * 16)

        self.sockets[0].listen(self.maxClients)
        self.Run()

    def __del__(self):
        for s in self.sockets[1:]:
            self.Close(s)

        self.sockets[0].close()

    def Close(self, sock : socket.socket):
        # Socket Already Closed
        if(sock not in self.sockets):
            return

        # Remove the socket
        self.sockets.remove(sock)
        id = sock.fileno()
        sock.close()
        
        # Kill and Close the Processes associated with this socket
        self.clientsProcesses[id][0].terminate()
        self.clientsProcesses[id][0].terminate()
        self.clientsProcesses[id][0].close()

        if(self.shared[id].driverPID.value != -1):
            # Terminate the selenium driver
            if(platform.system() == "Windows"):
                os.system(f"taskkill /F /T /PID {self.shared[id].driverPID.value}")
            else:
                os.kill(self.shared[id].driverPID.value, signal.SIGKILL)

        # Remove the socket from the dict
        del self.clientsProcesses[id]
        del self.shared[id]

    def Run(self):
        while True:
            read, write, error = select.select(self.sockets, self.sockets, self.sockets)
            
            for sock in read:
                sock : socket.socket
                if sock == self.sockets[0]:

                    client, addr = sock.accept()

                    if(len(self.clientsProcesses) >= self.maxClients):
                        client.send(CreateMessage(MessageTypes.ERROR_RESPONSE, SerializeError(ServerErrors.self.maxClients_REACHED)))
                        client.close()
                        continue

                    if addr[0] not in self.whitelist:
                        client.send(CreateMessage(MessageTypes.ERROR_RESPONSE, SerializeError(ServerErrors.NOT_IN_WHITELIST)))
                        client.close()
                        continue
                    
                    self.sockets.append(client)
                    apiP = APIProcess()
                    self.shared[client.fileno()] = Main2ProcessSharedVals()
                    self.clientsProcesses[client.fileno()] = (Process(target = apiP.Initialize, args = (client.fileno(), self.shared[client.fileno()], self.responses, self.debug,)), apiP)
                    self.clientsProcesses[client.fileno()][0].start()
                else:
                    msg = GetMessage(sock)
                    if(msg == None):
                        self.Close(sock)
                        continue
                    
                    msgType, msg = msg

                    if(msgType == MessageTypes.DEBUG):
                        if(self.debug):
                            self.Debug()
                            self.responses.put((CreateMessage(MessageTypes.DEBUG, b"1"), sock.fileno()))
                        else:
                            self.responses.put((CreateMessage(MessageTypes.ERROR_RESPONSE, SerializeError(ServerErrors.DEBUG_DISABLED)), sock.fileno()))
                        continue

                    with self.shared[sock.fileno()].lock:
                        self.shared[sock.fileno()].RequestType.value = msgType.value
                        self.shared[sock.fileno()].RequestData.value = msg
                        if(msgType == MessageTypes.INITIALIZE_GAME):
                            self.shared[sock.fileno()].TimeoutTime.value = time.time() + (self.timeoutTime * 2)
                        else:
                            self.shared[sock.fileno()].TimeoutTime.value = time.time() + self.timeoutTime

            for sock in error:
                self.Close(sock)

            self.CheckForTimeouts()

            for _ in range(self.responses.qsize()):
                msg, sockID = self.responses.get()
                sock = self.FindSocketByID(sockID)
                
                # Closed Socket
                if(sock == None):
                    continue
                
                # Socket is not ready to write
                if(sock not in write):
                    self.responses.put((msg, sockID))
                    continue
                
                try:
                    sock.send(msg)
                except:
                    self.Close(sock)

    def CheckForTimeouts(self):
        for id, share in self.shared.items():
            with share.lock:
                if(share.RequestType.value != -1 and share.TimeoutTime.value < time.time()):
                    self.responses.put((CreateMessage(MessageTypes.ERROR_RESPONSE, SerializeError(ServerErrors.TIMEOUT)), id))
                    share.RequestType.value = -1
                    share.TimeoutTime.value = 0
                    share.RequestData.value = b""

    def FindSocketByID(self, id : int):
        for sock in self.sockets:
            if(sock.fileno() == id):
                return sock
        return None

    def Debug(self):
        print("Number of Clients: ", len(self.clientsProcesses))

        print()
        print("Socket Data:")
        
        for sock in self.sockets[1:]:
            print("Socket Name: ", sock.getsockname())
            print("Socket ID: ", sock.fileno())
            print("Client IP: ", sock.getpeername()[0])
            print("Client Port: ", sock.getpeername()[1])

        print()
        print("Shared Data:")

        for id, share in self.shared.items():
            print("Client ID: ", id)
            print("Request Type: ", share.RequestType.value)
            print("Request Data: ", share.RequestData.value)
            print("Timeout Time: ", share.TimeoutTime.value)
        
        print()
        print("Process Data:")

        for id, p in self.clientsProcesses.items():
            print("Client ID: ", id)
            print("Process Alive: ", p[0].is_alive())
            print("Process ID: ", p[0])

class APIProcess:
    def __int__(self):
        self.api : SAP_API = None
        self.shared : Main2ProcessSharedVals = None
        self.responses : Queue = None
        self.id = -1

    def __del__(self):
        if(hasattr(self, "api")):
            del self.api

        if(hasattr(self, "shared")):
            del self.shared

    def Initialize(self, id : int, shared : Main2ProcessSharedVals, responses : Queue, debug : bool):
        self.id = id
        self.shared = shared
        self.responses = responses

        self.api = SAP_API(debug)
        self.shared.driverPID.value = self.api.driverPID
        responses.put((CreateMessage(MessageTypes.INIT, b"1"), self.id))

        self.Run()

    def Run(self):
        while True:
            if(self.shared.RequestType.value == -1):
                continue
            
            self.HandleMessage(MessageTypes(self.shared.RequestType.value), self.shared.RequestData.value)            

            with self.shared.lock:
                self.shared.RequestType.value = -1
                self.shared.RequestData.value = b''
                self.shared.TimeoutTime.value = 0

    def HandleMessage(self, msgType : MessageTypes, msg : bytearray):
        if(msgType == MessageTypes.INITIALIZE_GAME):
            self.api.InitializeGame()
            self.responses.put((CreateMessage(MessageTypes.INITIALIZE_GAME_RESPONSE, b"1"), self.id))
        elif(msgType == MessageTypes.GET_GAME_STATE):
            state = self.api.GetGameState()
            serializedState = state.Serialize()

            for i in range(len(serializedState)):
                self.responses.put((CreateMessage(MessageTypes(i + 4), serializedState[i]), self.id))

        elif(msgType == MessageTypes.PERFORM_ACTION):
            action, startSlot, endSlot = DeserializeAction(msg)
            status = self.api.PerformAction(action, startSlot, endSlot)
            self.responses.put((CreateMessage(MessageTypes.PERFORM_ACTION_RESPONSE, SerializeActionResponse(status, action, self.api.result)), self.id))
        else:
            self.responses.put((CreateMessage(MessageTypes.ERROR_RESPONSE, SerializeError(ServerErrors.INVALID_MESSAGE)), self.id))

