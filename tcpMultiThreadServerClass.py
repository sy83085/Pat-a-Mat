import socket
from dataheader import *


class TCPMultiThreadServer:
    def __init__(self, port : int = 2500, listener : int = 1):
        self.connected = False
        self.clients : dict[tuple[str, int], list[socket.socket, str]] = {}
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(('', port))
        self.sock.listen(listener)

    def disconnect(self, cAddr : tuple):
        if cAddr in self.clients:
            del self.clients[cAddr]
        if len(self.clients) == 0:
            self.connected = False
        print(self.clients)

    def accept(self):
        cSock, cAddr = self.sock.accept()
        self.connected = True
        self.clients[cAddr] = [cSock, ""]
        return cSock, cAddr

    def sendData(self, cSock : socket.socket, data : bytearray):
        if self.connected:
            cSock.sendall(len(data).to_bytes(4, "little"))
            cSock.sendall(data)
            return True
        else:
            return False

    def send(self, cSock : socket.socket, response):
        print(response)
        print(response.headerBytes)
        self.sendData(cSock, response.headerBytes)
        for dataByte in response.dataBytesList:
            print("dataByte : ", dataByte)
            self.sendData(cSock, dataByte)
        

    def receiveData(self, rSock : socket.socket = None):
        cAddr = rSock.getpeername()
        try:
            packet = rSock.recv(4)
            if not packet:
                raise
            dataSize = int.from_bytes(packet, "little")

            receiveBytes = bytearray()
            while len(receiveBytes) < dataSize:
                packetSize = 1024 if len(receiveBytes) + 1024 < dataSize else dataSize - len(receiveBytes)
                packet = rSock.recv(packetSize)
                if not packet:
                    raise
                receiveBytes.extend(packet)
            return receiveBytes
        except Exception as e:
            rSock.close()
            self.disconnect(cAddr)
            return None
    
    def receive(self, rSock : socket.socket = None):
        headerBytes = self.receiveData(rSock)
        if headerBytes is None:
            return (None, None)
        dataCount = int.from_bytes(headerBytes[0:4], "little")
        dataBytesList = list()
        for i in range(dataCount):
            receiveBytes = self.receiveData(rSock)
            if receiveBytes is None:
                return (None, None)
            dataBytesList.append(receiveBytes)
        return (headerBytes, dataBytesList)

    
    def processData(self, cSock : socket.socket, headerBytes : bytearray, dataBytesList : list[bytearray]):
        cAddr = cSock.getpeername()

        return ReqTextMessage(headerBytes, dataBytesList)
        
