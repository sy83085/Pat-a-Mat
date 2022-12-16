from tcpMultiThreadServerClass import TCPMultiThreadServer
from threading import Thread
import socket


def handler(server : TCPMultiThreadServer, cSock : socket.socket):
    while True:
        headerBytes, dataBytesList = server.receive(cSock)
        if headerBytes is None and dataBytesList is None:
            break
        reponse = server.processData(
            cSock=cSock, headerBytes=headerBytes, dataBytesList=dataBytesList
        )
        server.send(cSock, reponse)


server = TCPMultiThreadServer(port = 2500, listener = 100)   

while True:
    print("waiting for connection...")
    clientSock, addr = server.accept()
    cThread = Thread(target=handler, args=(server, clientSock))
    cThread.daemon = True
    cThread.start()
    print(server.clients)