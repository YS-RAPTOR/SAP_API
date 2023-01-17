import time
import socket
import select
from multiprocessing import Process, RLock, Queue

from SAP_API.API.SAP_API import SAP_API
from SAP_API.Common.ActionTypes import ActionTypes
from SAP_API.Common.ClientServer.Constants import *
from SAP_API.Common.ClientServer.Serialization import DeserializeAction, SerializeActionResponse, SerializeError
from SAP_API.Common.ClientServer.Messages import MessageTypes, ServerErrors
from SAP_API.Common.ClientServer.Communication import GetMessage, CreateMessage
class Server:
    
    def __init__(self, addr = "127.0.0.1", port = 5000, whitelist = ["127.0.0.1"]):
        self.whitelist = whitelist

        self.sockets : list[socket.socket] = [socket.socket(socket.AF_INET, socket.SOCK_STREAM)]
        self.sockets[0].bind((addr, port))
        
        self.clients : dict[socket.socket, tuple[SAP_API, Process, float]] = {}        
        self.clientsLock = RLock()

        self.responses = Queue(MAX_CLIENTS)
        
        self.timeoutProcess = Process(target = self.__TrackProcesses)
        self.timeoutProcess.start()
        self.sockets[0].listen()

        self.__Run()

    def __del__(self):
        for sock in self.sockets[1:]:
            self.__Close(sock)
            
        self.sockets[0].close()

        self.timeoutProcess.terminate()
        self.timeoutProcess.close()
        
    def __TrackProcesses(self):
        while True:
            for sock, data in self.clients.items():
                data : tuple[SAP_API, Process, float]
                # No process associated with this api
                if data[1] == None:
                    continue

                # Check to see if the process has finished
                if(not data[1].is_alive()):
                    # Close the process
                    self.clientsLock.acquire()
                    data[1].close()
                    self.clients[sock][1] = None
                    self.clients[sock][2] = None
                    self.clientsLock.release()
                    continue

                # Check to see if the process has been active for greater than TIMEOUT_TIME
                if(time.time() - data[2] > TIMEOUT_TIME):
                    # Terminate the process
                    self.clientsLock.acquire()
                    data[1].terminate()
                    data[1].close()
                    self.clients[sock][1] = None
                    self.clients[sock][2] = None
                    self.clientsLock.release()

                    # Send an error message to the client
                    self.responses.put((CreateMessage(MessageTypes.ERROR_RESPONSE, SerializeError(ServerErrors.TIMEOUT)), sock))
                    continue
    
    def __Run(self):
        while True:
            # Wait for a client to connect
            read, write, error = select.select(self.sockets, self.sockets, self.sockets)
            for sock in read:
                sock : socket.socket
                if sock == self.sockets[0]:

                    client, addr = sock.accept()

                    if(len(self.clients) >= MAX_CLIENTS):
                        client.send(CreateMessage(MessageTypes.ERROR_RESPONSE, SerializeError(ServerErrors.MAX_CLIENTS_REACHED)))
                        client.close()
                        continue

                    if addr[0] not in self.whitelist:
                        client.send(CreateMessage(MessageTypes.ERROR_RESPONSE, SerializeError(ServerErrors.NOT_IN_WHITELIST)))
                        client.close()
                        continue

                    # Add the client to the list of clients
                    self.clientsLock.acquire()
                    self.clients[sock] = (None, None, None)
                    self.clientsLock.release()
                    self.sockets.append(client)
                    self.__AddProcess(client, Process(target = self.__AddClient, args = (client,)))

                else:
                    # Handle Messages
                    if (self.__HandleMessage(sock)):
                        self.__Close(sock)
                    
            for sock in error:
                sock : socket.socket
                # Remove the client from the list of clients
                self.__Close(sock)

            for _ in range(self.responses.qsize()):
                msg, sock = self.responses.get()
                
                # Socket is closed 
                if sock not in self.sockets:
                    continue
                
                # Socket is not ready to send data
                if sock not in write:
                    self.responses.put((msg, sock))
                    continue
                
                # Send the message
                sock.send(msg)
    
    def __Close(self, sock : socket.socket):
        # Check to see if the socket is in the list of sockets. If it is not, then it has already been closed
        if(sock not in self.sockets):
            return

        self.clientsLock.acquire()

        # Check to see if their is a process running
        if self.clients[sock][1] != None:
            if(self.clients[sock][1].is_alive()):
                # Terminate Process if Running
                self.clients[sock][1].terminate()
                
            # Close Process
            self.clients[sock][1].close()
        
        self.sockets.remove(sock)

        # Close Socket
        sock.close()

        # Remove Client from List and free api
        del self.clients[sock]
        
        self.clientsLock.release()

    def __AddProcess(self, sock : socket.socket, process : Process) -> bool:

        self.clientsLock.acquire()

        # Check to see if their is already a process running
        if self.clients[sock][1] != None:
            self.clientsLock.release()
            return False

        self.clients[sock][1] = process
        self.clients[sock][2] = time.time()
        self.clientsLock.release()

        return True

    def __AddClient(self, sock : socket.socket):
        # Create a new SAP_API
        api = SAP_API()
        
        self.clientsLock.acquire()
        self.clients[sock][0] = api
        self.clientsLock.release()

        # Send Response to client INIT_R
        self.responses.put((CreateMessage(MessageTypes.INIT, b"1"), sock))

    def __HandleMessage(self, sock : socket.socket) -> bool:
        msg = GetMessage(sock)

        if(msg == None):
            return False
        
        msgType, msg = msg
        self.__AddProcess(sock, Process(target = self.__EvaluateMessage, args = (msgType, msg, sock)))
        
    def __EvaluateMessage(self, msgType : MessageTypes, msg : bytearray, sock : socket.socket):
        api = self.clients[sock][0]
        if(msgType == MessageTypes.INITIALIZE_GAME):
            api.InitializeGame()
            self.responses.put((CreateMessage(MessageTypes.INITIALIZE_GAME_RESPONSE, b"1"), sock))
        elif(msgType == MessageTypes.GET_GAME_STATE):
            state = api.GetGameState()
            self.responses.put((CreateMessage(MessageTypes.GET_GAME_STATE_RESPONSE, state.Serialize()), sock))
        elif(msgType == MessageTypes.PERFORM_ACTION):
            actionType, start, end = DeserializeAction(msg)
            status = api.PerformAction(actionType, start, end)
            self.responses.put((CreateMessage(MessageTypes.PERFORM_ACTION_RESPONSE, SerializeActionResponse(status, actionType, api.result)), sock))
        else:
            self.responses.put((CreateMessage(MessageTypes.ERROR_RESPONSE, SerializeError(ServerErrors.INVALID_MESSAGE)), sock))
            return
