from enum import Enum


class RequestType(Enum):
    TextMessage = 2

class ResponseType(Enum):
    TextMessage = 2

class Request:
    def __init__(self, headerBytes : bytearray, dataBytesList : list[bytearray]):
        self.headerBytes = headerBytes
        self.dataBytesList = dataBytesList
        self.dataCount = int.from_bytes(headerBytes[0:4], "little")
        self.type = int.from_bytes(headerBytes[4:8], "little")
        self.attrSize = int.from_bytes(headerBytes[8:12], "little")

class ReqTextMessage:
    def __init__(self, headerBytes : bytearray, dataBytesList : list[bytearray]):
        super().__init__()
        self.textMessage = dataBytesList[0].decode()
        # print(self.textMessage)
        


####
class Response:
    def init(self):
        self.headerBytes : bytearray = bytearray()
        self.dataBytesList : list[bytearray] = list()

    def totalDataSize(self):
        totalDataSize = 0
        for dataBytes in self.dataBytesList:
            totalDataSize += len(dataBytes)
        return totalDataSize

class ResText(Response):
    def __init__(self, msg : str):
        super().__init__()
        self.headerBytes.extend(int(1).to_bytes(4, "little"))
        self.headerBytes.extend(ResponseType.TextMessage.value.to_bytes(4, "little"))
        self.dataBytesList.append(msg.encode())
        self.headerBytes.extend(self.totalDataSize().to_bytes(4, "little"))