#!/usr/bin/env python3

from socket import *
from sys import *

if __name__ == '__main__':

    if len(argv) != 3:
        print("Wrong input format!")
        print("Usage: ./client.py <prox-port> <proxy-ip> ")
        exit(0)

    serverPort = int(argv[1])
    serverIp = argv[2]
    clientSocket = socket(AF_INET, SOCK_STREAM)
    try:
        clientSocket.connect((serverIp, serverPort))
    except:
        print("connection error!\nunavailable port or unavailable Ip!")
        exit(0)

    while True:
        sendInfo = input("message sent from client (enter exit to disconnect)：")
        if not sendInfo:
            continue
        clientSocket.send(sendInfo.encode())  # socket transport byte data
        if sendInfo == "exit":
            print("connection end！")
            break
        receivedInfo = clientSocket.recv(2048).decode()
        print("the message sent from server：{}".format(receivedInfo))
        print("---------------------------------")

    clientSocket.close()
