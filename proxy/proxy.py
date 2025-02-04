#!/usr/bin/env python3.10

import os, threading, time, sys
from socket import *

serverPort = 8080
T_dict = {"Default": 1000.0}
# use a global dictionary to store the EWMA for each "<client-ip>, <server-ip>"
# the key store a string variable - combination of client-ip and server-ip like "127.0.0.1 4.0.0.1"
# the value store a float variable - throughput of each connection
nolist = ""  # use nolist to denote the content of nolist.mpd, which will be used to adjust the bitrate


def proxyListen():
    global T_dict
    if len(sys.argv) != 6:
        print("Wrong input format!")
        print("Usage: ./proxy <log> <alpha> <listen-port> <fake-ip> <web-server-ip>")
        return False
    else:
        logFile = sys.argv[1]
        alpha = float(sys.argv[2])
        listen_port = int(sys.argv[3])
        localIp = sys.argv[4]
        serverIP = sys.argv[5]

    log = open(logFile, 'w+')

    browserSocket = socket(AF_INET, SOCK_STREAM)
    browserSocket.bind(('', int(listen_port)))  # bind to INADDR_ANY ''
    browserSocket.listen(5)
    print("wait for connection")

    while True:
        try:
            connection, address = browserSocket.accept()
            # print(address[0])
            # print(type(serverIP))
            key = address[0] + serverIP  # address is a tuple
            if key in T_dict.keys():
                T = T_dict.get(key)
            else:
                T = T_dict.get("Default")
                T_dict[key] = T
            t = threading.Thread(target=proxy, args=(connection, serverIP, localIp, alpha, log, T, key))
            t.start()
        except KeyboardInterrupt:
            browserSocket.close()
            log.close()
            print("KeyboardInterrupt: Exit")
            break

    log.close()

    return


def proxy(connection, serverIp, localIp, alpha, log, T, key):
    global serverPort, nolist
    request = connection.recv(2048).decode()  # receiving packets from clients
    throughput = T  # guarantee that the throughput would not change in this thread

    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind((localIp, 0))
    serverSocket.connect((serverIp, serverPort))

    if request.find("GET") != -1:
        request_split = request.split(' ')  # split request file by '\n'
        url = request_split[1]  # get the url- the second part
        if url.find("BigBuckBunny_6s.mpd") != -1:  # if clinet request 6s.mpd
            serverSocket.send(request.encode())  # firstly send a request for 6s.mpd
            mpd = serverSocket.recv(2048)  # get the content of 6s.mpd, but don't return
            nolist = str(mpd)  # store the content in nolist
            urlNew = url.replace("BigBuckBunny_6s.mpd", "BigBuckBunny_6s_nolist.mpd")  # modify request for 6s_nolist.mpd
            bitrate = 1000  # label
            request = request.replace("BigBuckBunny_6s.mpd", "BigBuckBunny_6s_nolist.mpd")  # modify the request
        elif url.find('bps/BigBuckBunny') != -1:
            urlNew, bitrate = ABR(url, throughput)  # use ABR to update the request for a suitable chunk
            request = request.replace(url, urlNew)
        else:
            urlNew = url
            bitrate = 1000
        times = time.time()  # start time
        serverSocket.send(request.encode())  # send the request to the server
    else:
        return

    curSize = 0
    totalSize = 0
    # print("return video chunk...")
    while True:  # the size of chunk may exceed the size of receive buffer, so we use a while loop to receive the chunk
        try:
            if curSize == 0:
                chunks = serverSocket.recv(2048)
                connection.send(chunks)
                recv = str(chunks)
                index = recv.find("Content-Length: ")  # find the "Content-Length" label
                indexHeader = recv.find(r"\r\n\r\n") - 18  # find the end of the header
                curSize = len(chunks)
                if index != -1:
                    index_split = recv[index:].split(r"\r\n")
                    totalSize = int(index_split[0][16:]) + indexHeader
                    # print("content-length: ", int(index_split[0][16:]))
                    # print()
                    # print("header size: ", indexHeader)
                    # print("total size of the chunk: ", totalSize)
            elif curSize < totalSize:
                chunks = serverSocket.recv(8192)
                if len(chunks) == 0:
                    duration = time.time() - times
                    break
                connection.send(chunks)
                curSize += len(chunks)
                # print(curSize)
            else:  # if the size of received data equals to or larger than the expected size of chunks, break
                duration = time.time() - times  # stop the timer when received enough lengths of content
                break
        except KeyboardInterrupt:
            print("KeyboardInterrupt: Exit")
            serverSocket.close()
            connection.close()
            sys.exit(1)
    # print("return finished")

    curThroughput = curSize * 8 / (1000 * duration)
    T = (1 - alpha) * T + alpha * curThroughput
    log_string = str(int(time.time())) + ' ' + str(
        duration) + ' ' + '%.0f' % curThroughput + ' ' + '%.0f' % throughput + ' ' + "%d" % int(bitrate/1000) + ' ' + str(
        serverIp) + ' ' + urlNew + '\n'
    log.write(log_string)
    T_dict[key] = T  # update or add the client-server and its throughput to global dictionary variable

    serverSocket.close()
    connection.close()
    return


def ABR(url, throughput):  # modify the url according to throughput
    global nolist
    maxBR = throughput * 1000 / 1.5  # the maximum bitrate
    # print()
    # print(maxBR)
    urlNew = url
    throughputNew = throughput
    # url = ".../bunny_1006743bps/BigBuckBunny_6s3.m4s"
    indexStart = url.find("bunny_")
    indexEnd = url.find("bps")
    bitrate = url[indexStart + len("bunny_"): indexEnd]

    # print(type(nolist))
    # print(nolist)
    attribute = nolist.split("media=\"")
    # print(attribute[1])
    media = attribute[1].split(r"\n")
    i = len(media)
    while i > 1:
        i -= 1
        indexStartMedia = media[i].find("bandwidth=\"")  # find the index of "bandwidth" attribute
        if indexStartMedia != -1:
            indexEndMedia = media[i].find("\" />")
            bitrateMedia = media[i][indexStartMedia + len("bandwidth=\""): indexEndMedia]
            # print(bitrateMedia)
            if int(bitrateMedia) < maxBR:
                urlNew = url.replace(bitrate, bitrateMedia)
                # print(bitrateMedia)
                return urlNew, int(bitrateMedia)
            elif i == 1:
                urlNew = url.replace(bitrate, bitrateMedia)
                return urlNew, int(bitrateMedia)
        else:
            continue

    return urlNew, throughputNew


if __name__ == '__main__':
    proxyListen()
    exit(1)
