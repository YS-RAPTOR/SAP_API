from SAP_API.Common.Results import Results
from SAP_API.Common.ActionTypes import ActionTypes
from SAP_API.Common.ClientServer.Messages import ServerErrors

def SerializeAction(type : ActionTypes, start, end) -> bytearray:
    return f"{type.value},{start},{end}".encode("utf-8")

def SerializeActionResponse(status : bool, actionType : ActionTypes, result : Results) -> bytearray:
    msg = f"{int(status)}"
    # Check if the actionType is EndTurn
    if(actionType == ActionTypes.END):
        msg += f",{result.value}"

    return msg.encode("utf-8")

def SerializeError(error : ServerErrors) -> bytearray:
    return str(error.value).encode("utf-8")

def DeserializeAction(msg : bytearray) -> tuple[ActionTypes, int, int]:
    msg = msg.decode("utf-8")
    type, start, end = msg.split(",")
    return (ActionTypes(int(type)), int(start), int(end))

def DeserializeActionResponse(msg : bytearray) -> tuple[bool, Results]:
    msg = msg.decode("utf-8")

    # Has Only Status
    if(msg.find(",") == -1):
        return (bool(int(msg)), None)

    # Has Status and Result
    status, result = msg.split(",")
    return (bool(int(status)), Results(int(result)))

def DeserializeError(msg : bytearray) -> ServerErrors:
    return ServerErrors(int(msg.decode("utf-8")))