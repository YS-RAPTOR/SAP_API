import socket
from SAP_API.Common.ClientServer.Messages import MessageTypes
from SAP_API.Common.ClientServer.Constants import *

def GetMessage(sock : socket.socket) -> tuple[MessageTypes, bytearray]:
    # Catch Force closes
    try:
        header = sock.recv(FIXED_HEADER_LENGTH)
    except:
        return None

    if len(header) == 0:
        return None

    header = header.decode("utf-8")
    msgLength = int(header[:16])
    msgType = MessageTypes(int(header[16:]))
    
    msg = b""
    i = 0
    while i < msgLength:
        if(msgLength - i < BUFFER_SIZE):
            msg += sock.recv(msgLength - i)
        else:
            msg += sock.recv(BUFFER_SIZE)

        i += BUFFER_SIZE

    if len(msg) != msgLength:
        return None

    return msgType, msg

def CreateMessage(msgType : MessageTypes, msg : bytearray) -> bytearray:
    header = bytearray(f"{len(msg):016d}{msgType.value:016d}", "utf-8")
    return header + msg

    