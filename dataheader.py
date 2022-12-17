from enum import Enum

class Request:
    def __init__(self, headerBytes : bytearray, dataBytesList : list[bytearray]):
        self.headerBytes = headerBytes
        self.dataBytesList = dataBytesList
        self.dataCount = int.from_bytes(headerBytes[0:4], "little")
        self.attrSize = int.from_bytes(headerBytes[4:8], "little")

class ReqTextMessage:
    def __init__(self, headerBytes : bytearray, dataBytesList : list[bytearray]):
        super().__init__()
        self.textMessage = dataBytesList[0].decode()
        


####
class Response:
    def __init__(self):
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
        print(1234)
        print(msg)
        self.headerBytes.extend(int(1).to_bytes(4, "little"))
        self.headerBytes.extend(int(1).to_bytes(4, "little"))
        self.headerBytes.extend(len(msg).to_bytes(4, "little"))
        dataBytes = bytearray()

        sendmsg = msg.encode()
        print("sendmsg : ", sendmsg)
        dataBytes.extend(sendmsg)
        print("dataBytes : ", dataBytes)
        self.dataBytesList.append(dataBytes)
        print(self.dataBytesList)
