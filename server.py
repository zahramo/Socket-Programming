from socket import *
import json
import _thread

###----function definitions----###
def serveClient(commandSocket, dataSocket):
    userLoggedIn = False
    while True:
        command = commandSocket.recv(10000).decode('utf-8')
        data = dataSocket.recv(10000).decode('utf-8')

        if(command == "USER"):
            username = data
            commandSocket.send("331 User name okay, need password.".encode('utf-8'))
            if(commandSocket.recv(10000).decode('utf-8') == "PASS"):
                password = dataSocket.recv(10000).decode('utf-8')
                for user in config['users']:
                    if(user['user'] == username and user['password'] == password):
                        userLoggedIn = True
                        commandSocket.send("230 User logged in, proceed.".encode('utf-8'))
                        continue
                if(userLoggedIn == False):
                    commandSocket.send("430 Invalid username or password.".encode('utf-8'))
                    continue
        if(command == "PASS"):
            commandSocket.send("503 Bad sequence of commands.".encode('utf-8'))
            continue


        if(userLoggedIn == False):
            commandSocket.send("332 Need account for login.".encode('utf-8'))
            continue
        else:
            if(command == "QUIT"):
                userLoggedIn = False
                break
            else:
                commandSocket.send("500 Error.".encode('utf-8'))
         
        

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