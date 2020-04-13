from socket import *
import json

# with open('../config.json', 'r') as file:
#     config = json.load(file)

# commandPort = config['commandChannelPort']
commandPort = 8000
commandSocket = socket(AF_INET, SOCK_STREAM)
commandSocket.connect(('127.0.0.1',commandPort))

# dataPort = config['dataChannelPort']
dataPort = 8001
dataSocket = socket(AF_INET, SOCK_STREAM)
dataSocket.connect(('127.0.0.1',dataPort))

while True:
    buffer = input().split()
    command = buffer[0]
    data = "@"

    ## command channel responses ##
    if (command == "USER" or command == "PASS" or
        command == "PWD" or command == "CWD" or
        command == "HELP" or command == "QUIT") :
        if(len(buffer) == 2):
            data = buffer[1]
        commandSocket.send(command.encode('utf-8'))
        dataSocket.send(data.encode('utf-8'))
        commandResponse = commandSocket.recv(10000).decode('utf-8')
        print(commandResponse)

    ## data channel responses ##
    elif(command == "LIST"):
        if(len(buffer) == 2):
            data = buffer[1]
        commandSocket.send(command.encode('utf-8'))
        dataSocket.send(data.encode('utf-8'))
        dataResponse = dataSocket.recv(10000).decode('utf-8')
        commandResponse = commandSocket.recv(10000).decode('utf-8')
        print(commandResponse)
        if(dataResponse != "@" and data == "@"):
            print(dataResponse)
    elif(command == "DL"):
        if(len(buffer) == 2):
            data = buffer[1]
        commandSocket.send(command.encode('utf-8'))
        dataSocket.send(data.encode('utf-8'))
        dataResponse = dataSocket.recv(10000)
        if(dataResponse != "@" and data != "@"):
            file = open(data, 'wb')
            file.write(dataResponse)
            file.close()
        commandResponse = commandSocket.recv(10000).decode('utf-8')
        print(commandResponse)

    ## commands with flag ##
    elif(command == "MKD" or command == "RMD"):
        if(len(buffer) == 2):
            data = buffer[1]
        elif(len(buffer) == 3):
            command = buffer[0] + buffer[1]
            data = buffer[2]
        commandSocket.send(command.encode('utf-8'))
        dataSocket.send(data.encode('utf-8'))
        commandResponse = commandSocket.recv(10000).decode('utf-8')
        print(commandResponse)

    ## invalid commands ##    
    else:
        commandSocket.send(command.encode('utf-8'))
        dataSocket.send(data.encode('utf-8'))
        commandResponse = commandSocket.recv(10000).decode('utf-8')
        print(commandResponse)

commandSocket.close()
dataSocket.close()

