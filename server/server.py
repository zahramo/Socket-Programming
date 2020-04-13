from socket import *
import json
import _thread
import os
import shutil

###----function definitions----###
def serveClient(commandSocket, dataSocket):
    userLoggedIn = False
    while True:
        command = commandSocket.recv(10000).decode('utf-8')
        data = dataSocket.recv(10000).decode('utf-8')

        print(command, data)

        if(checkCommandValidation(command, data) == False):
            if(command == "LIST" or command == "DL"):
                dataSocket.send(("@").encode('utf-8'))
            commandSocket.send("501 Syntax error in parameters or arguments.".encode('utf-8'))
            continue

        if(command == "USER"):
            username = data
            commandSocket.send("331 User name okay, need password.".encode('utf-8'))
            if(commandSocket.recv(10000).decode('utf-8') == "PASS"):
                password = dataSocket.recv(10000).decode('utf-8')
                for user in config['users']:
                    if(user['user'] == username and user['password'] == password):
                        userLoggedIn = True
                        commandSocket.send("230 User logged in, proceed.".encode('utf-8'))
                        break
                if(userLoggedIn == False):
                    commandSocket.send("430 Invalid username or password.".encode('utf-8'))
                continue
        if(command == "PASS"):
            commandSocket.send("503 Bad sequence of commands.".encode('utf-8'))
            continue

        if(command == "HELP"):
            USER = "USER [name], Its argument is used to specify the user's string. It is used for user authentication.\n"
            PWD = "PWD, It is used for displaying current directory.\n"
            MKD = "MKD -i [name], Its argument is used to specify the directory/file name. when -i is used, arguments specifies as file, else as a directory. It is used for making directory/file.\n"
            RMD = "RMD -i [name], Its argument is used to specify the directory/file name. when -i is used, arguments specifies as file, else as a directory. It is used for removing directory/file.\n"
            LIST = "LIST, It is used for displaying files in current directory.\n"
            DL = "DL [name], Its argument is used to specify the file name. It is used for downloading file.\n"
            QUIT = "QUIT, It is used for exiting from server."
            HELP = USER + PWD + MKD + RMD + LIST + DL + QUIT                                                                                                                                                                                                                                                                                                                    
            commandSocket.send(("214\n" + HELP).encode('utf-8')) 

        if(userLoggedIn == False):
            commandSocket.send("332 Need account for login.".encode('utf-8'))
            continue
        else:
            if(command == "PWD"):
                commandSocket.send(("257 " + os.getcwd()).encode('utf-8'))

            elif(command == "MKD"):
                if(os.path.isdir(data)):
                    commandSocket.send(("500 Error.").encode('utf-8'))
                else:                    
                    os.mkdir(data)
                    commandSocket.send(("257 " + os.getcwd() + "\\" + data + " created.").encode('utf-8'))

            elif(command == "MKD-i"):
                if(os.path.isfile(data)):
                    commandSocket.send(("500 Error.").encode('utf-8'))
                else:                     
                    file = open(data, 'w')
                    file.close()
                    commandSocket.send(("257 " + os.getcwd() + "\\" + data + " created.").encode('utf-8'))

            elif(command == "RMD"):
                if(os.path.isdir(data) == False):
                    commandSocket.send(("500 Error.").encode('utf-8'))
                else:                 
                    shutil.rmtree(data)
                    commandSocket.send(("250 " + os.getcwd() + "\\" + data + " deleted.").encode('utf-8'))

            elif(command == "RMD-f"):
                if(os.path.isfile(data) == False):
                    commandSocket.send(("500 Error.").encode('utf-8'))
                else:                     
                    os.remove(data)
                    commandSocket.send(("257 " + os.getcwd() + "\\" + data + " deleted.").encode('utf-8'))

            elif(command == "LIST"):
                delim = " "
                dataSocket.send((delim.join(os.listdir())).encode('utf-8'))  
                commandSocket.send(("226 List transfer done.").encode('utf-8'))

            elif(command == "CWD"):
                if(os.path.isdir(data) == False):
                    commandSocket.send(("500 Error.").encode('utf-8'))
                else:      
                    os.chdir(data)
                    commandSocket.send(("250 Successful Change.").encode('utf-8'))   

            elif(command == "DL"):
                if(os.path.isfile(data) == False):
                    dataSocket.send(("@").encode('utf-8'))                      
                    commandSocket.send(("500 Error.").encode('utf-8'))
                else:
                    file = open(data, 'rb')
                    dataSocket.send(file.read())
                    file.close()                      
                    commandSocket.send(("226 Successful Download.").encode('utf-8'))

            elif(command == "QUIT"):
                userLoggedIn = False
                dataSocket.close()
                commandSocket.close()
                break
            else:
                commandSocket.send("501 Syntax error in parameters or arguments.".encode('utf-8'))
         
        
def checkCommandValidation(commad, data):
    if(commad == "USER" and data != "@"): return True
    if(commad == "PASS" and data != "@"): return True
    if(commad == "PWD" and data == "@"): return True
    if(commad == "MKD" and data != "@"): return True
    if(commad == "MKD-i" and data != "@"): return True
    if(commad == "RMD" and data != "@"): return True
    if(commad == "RMD-i" and data != "@"): return True
    if(commad == "LIST" and data == "@"): return True
    if(commad == "CWD" and data != "@"): return True
    if(commad == "DL" and data != "@"): return True
    if(commad == "HELP" and data == "@"): return True
    if(commad == "QUIT" and data == "@"): return True
    return False

###-------------main-----------### 
config = {}
with open('config.json', 'r') as file:
    config = json.load(file)

commandPort = config['commandChannelPort']
dataPort = config['dataChannelPort']

commandSocket = socket(AF_INET, SOCK_STREAM)
commandSocket.bind(("",commandPort))
commandSocket.listen(5)
dataSocket = socket(AF_INET, SOCK_STREAM)
dataSocket.bind(("",dataPort))
dataSocket.listen(5)


while True:
    clientCommandSocket,a = commandSocket.accept()
    clientDataSocket,a = dataSocket.accept()

    print("Recieved connection from" , a)
    _thread.start_new_thread(serveClient, (clientCommandSocket,clientDataSocket))
 
commandSocket.close()
dataSocket.close()