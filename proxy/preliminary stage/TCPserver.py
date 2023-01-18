#!/usr/bin/env python3

from socket import *

if __name__ == '__main__':

    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(("127.0.0.1", 8080))  # Bind the service address on the server
    serverSocket.listen(5)  # Listen for connection requests

    while True:
        print("waiting for connection...")
        conn, addr = serverSocket.accept()  # Waiting for connection from client
        print("connected")
        while True:
            clientData = conn.recv(2048).decode()
            if clientData == "exit":
                break
            print("Message sent by client from %s: %s" % (addr, clientData))
            serverData = input("message sent from server：")
            conn.send(serverData.encode())
        conn.close()
        print("disconnected with proxy")
        print("---------------------------------")

