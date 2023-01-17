import socket
from SAP_API.Common.ClientServer.Messages import MessageTypes
from SAP_API.Common.ClientServer.Constants import *

def GetMessage(sock : socket.socket) -> tuple[MessageTypes, bytearray]:
    header = sock.recv(FIXED_HEADER_LENGTH)
    if len(header) == 0:
        return None

    header = header.decode("utf-8")
    msgLength = int(header[:16])
    msgType = MessageTypes(header[16:].strip())
    
    msg = b""
    i = 0
    while i < msgLength:
        msg += sock.recv(BUFFER_SIZE)
        i += BUFFER_SIZE

    if len(msg) != msgLength:
        return None

    return msgType, msg

def CreateMessage(msgType : MessageTypes, msg : bytearray) -> bytearray:
    header = bytearray(f"{len(msg):016d}{msgType.value:16}", "utf-8")
    return header + msg


    