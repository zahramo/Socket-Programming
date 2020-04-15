from socket import *
import json
import _thread
import os
import shutil
from datetime import datetime
import base64
import time

###----function definitions----###

def createLogFile():
    logging = config['logging']
    if(logging['enable'] == True):
        file = open(logging['path'], 'a+')
        file.close()
        return logging['path']
    return ''

def isUserAdmin(username):
    authorization = config['authorization']
    if(authorization['enable']):
        for user in authorization['admins']:
            if(user == username):
                return True
        return False
    else:
        return True

def isFilePrivate(filename):
    authorization = config['authorization']
    for name in authorization['files']:
        if(name == filename):
            return True
    return False

def log(msg):
    if(logFile != ''):
        now = datetime.now()
        dt_string = now.strftime("%B %d, %Y %H:%M:%S")
        file = open(logFile, 'a')
        file.write(msg + dt_string + '\n')
        file.close()

def doesUserNameExist(username):
    for user in config['users']:
        if(user['user'] == username):
            return True
    return False    

def isPasswordCorrect(username, password):
    for user in config['users']:
        if(user['user'] == username and user['password'] == password):
            return True
    return False

def getDownloadStatus(fileName, username):
    size = os.path.getsize(fileName)
    accounting = config['accounting']
    for user in accounting['users']:
        if(user['user'] == username):
            userSize = int(user['size'])
            if(userSize < size):
                return False
            userSize -= size
            user['size'] = str(userSize)
            configFile = open("config.json", "w")
            json.dump(config, configFile)
            configFile.close()
            return True

def handleMail(username):
    print(username)
    accounting = config['accounting']
    threshold = int(accounting['threshold'])
    for user in accounting['users']:
        print(user['user'])
        if(user['user'] == username):
            print('same')
            if(user['alert'] == True):
                print('alert')
                userSize = int(user['size'])
                print(userSize)
                print(threshold)
                if(userSize < threshold):
                    print(userSize)
                    print(threshold)
                    sendEmail(user['email'], user['user'])

def sendEmail(emailAddr, username):
    mailserver = ("mail.ut.ac.ir", 25)
    mailSocket = socket(AF_INET, SOCK_STREAM)
    mailSocket.connect(mailserver)
    serverMessages = []
    serverMessages.append(mailSocket.recv(1024).decode('utf-8'))
    print("Server message after connection request:" + serverMessages[0])
    messageStatus = serverMessages[0][:3]
    if messageStatus != '220':
        print("Can't connect to mail server")
    else :
        helloCommand = 'EHLO mail.ut.ac.ir\r\n'
        mailSocket.send(helloCommand.encode('utf-8'))
        serverMessages.append(mailSocket.recv(1024).decode('utf-8'))
        print("Message after EHLO command:" + serverMessages[1])
        messageStatus = serverMessages[1][:3]
        if messageStatus != '250':
            print('Server does not say hello back.')
        else:
            authenticationData = b'AHphaHJhLm1vb3NhdmkubW8AU3phaHJhbW85OQ=='
            authMsg = "AUTH PLAIN ".encode('utf-8')+authenticationData+"\r\n".encode('utf-8')
            mailSocket.send(authMsg)
            serverMessages.append(mailSocket.recv(1024).decode('utf-8'))
            print("Server message after auth request:" + serverMessages[2])

            mailFrom = "MAIL FROM:<zahra.moosavi.mo@ut.ac.ir>\r\n"
            mailSocket.send(mailFrom.encode('utf-8'))
            serverMessages.append(mailSocket.recv(1024).decode('utf-8'))
            print("Server message after mail from request:" + serverMessages[3])

            rcptTo = "RCPT TO:<moosavizahra67@yahoo.com>\r\n"
            mailSocket.send(rcptTo.encode('utf-8'))
            serverMessages.append(mailSocket.recv(1024).decode('utf-8'))
            print("Server message after recp to request: "+serverMessages[4])

            data = "DATA\r\n"
            mailSocket.send(data.encode('utf-8'))
            serverMessages.append(mailSocket.recv(1024).decode('utf-8'))
            print("Server message after DATA request: " + serverMessages[5])

            msg = "\r\n Hello " + username + "! please check your account. your account volume is less than threshold."
            endmsg = "\r\n.\r\n"
            subject = "Subject: Not enough volume\r\n\r\n" 
            mailSocket.send(subject.encode('utf-8'))
            date = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())
            date = date + "\r\n\r\n"
            mailSocket.send(date.encode('utf-8'))
            mailSocket.send(msg.encode('utf-8'))
            mailSocket.send(endmsg.encode('utf-8'))
            serverMessages.append(mailSocket.recv(1024).decode('utf-8'))
            print("Server message after sending message body:"+serverMessages[6])
            log("An alert mail sent to " + username)
            quit = "QUIT\r\n"
            mailSocket.send(quit.encode('utf-8'))
            serverMessages.append(mailSocket.recv(1024).decode('utf-8'))
            print("Server message after quit:"+serverMessages[7])
            mailSocket.close()

def serveClient(commandSocket, dataSocket):
    userLoggedIn = False
    userName = ''
    passWord = ''
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

            if(not doesUserNameExist(username)):
                commandSocket.send("430 Invalid username or password.".encode('utf-8'))
                continue

            commandSocket.send("331 User name okay, need password.".encode('utf-8'))
            userName = username
            command = commandSocket.recv(10000).decode('utf-8')
            if(command == "PASS"):
                password = dataSocket.recv(10000).decode('utf-8')
                if(not isPasswordCorrect(username, password)):
                    commandSocket.send("430 Invalid username or password.".encode('utf-8'))
                    continue
                userLoggedIn = True
                passWord = password
                isAdmin = isUserAdmin(userName)
                log(userName + " entered the system at ")
                commandSocket.send("230 User logged in, proceed.".encode('utf-8'))
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
            dataSocket.send("@".encode('utf-8'))
            continue
        else:
            if(command == "PWD"):
                commandSocket.send(("257 " + os.getcwd()).encode('utf-8'))

            elif(command == "MKD"):
                if(os.path.isdir(data)):
                    commandSocket.send(("500 Error.").encode('utf-8'))
                else:                    
                    os.mkdir(data)
                    log(userName + " made " + os.getcwd() + "/" + data + " directory at ")
                    commandSocket.send(("257 " + os.getcwd() + "/" + data + " created.").encode('utf-8'))

            elif(command == "MKD-i"):
                if(os.path.isfile(data)):
                    commandSocket.send(("500 Error.").encode('utf-8'))
                else:                     
                    file = open(data, 'w')
                    file.close()
                    log(userName + " made " + data + " file at ")
                    commandSocket.send(("257 " + data + " created.").encode('utf-8'))

            elif(command == "RMD"):
                if(os.path.isfile(data) == False):
                    commandSocket.send(("500 Error.").encode('utf-8'))
                else:       
                    if(not isAdmin):
                        if(isFilePrivate(data)):
                            commandSocket.send(("550 File unavailable.").encode('utf-8'))
                            continue
                    os.remove(data)
                    log(userName + " deleted " + data + " file at ")
                    commandSocket.send(("257 " + data + " deleted.").encode('utf-8'))
            elif(command == "RMD-f"):
                if(os.path.isdir(data) == False):
                    commandSocket.send(("500 Error.").encode('utf-8'))
                else:                 
                    shutil.rmtree(data)
                    log(userName + " deleted " + os.getcwd() + "/" + data + " directory at ")
                    commandSocket.send(("250 " + os.getcwd() + "/" + data + " deleted.").encode('utf-8'))

            elif(command == "LIST"):
                delim = " "
                dataSocket.send((delim.join(os.listdir())).encode('utf-8'))  
                commandSocket.send(("226 List transfer done.").encode('utf-8'))

            elif(command == "CWD"):
                if(data == '@'):
                    data = serverDirectory
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
                    if(not isAdmin):
                        if(isFilePrivate(data)):
                            dataSocket.send(("@").encode('utf-8')) 
                            commandSocket.send(("550 File unavailable.").encode('utf-8'))
                            continue
                    if(getDownloadStatus(data, userName)):
                        file = open(data, 'rb')
                        dataSocket.send(file.read())
                        file.close()       
                        log(userName + " downloaded " + data + " file at ")
                        commandSocket.send(("226 Successful Download.").encode('utf-8'))
                    else:
                        dataSocket.send(("@").encode('utf-8'))                      
                        commandSocket.send(("425 Can't open data connection.").encode('utf-8'))
                    handleMail(userName)

            elif(command == "QUIT"):
                userLoggedIn = False
                log(userName + " quit the system at ")
                commandSocket.send("221 Successful Quit.".encode('utf-8'))
                continue
                # break
            else:
                commandSocket.send("501 Syntax error in parameters or arguments.".encode('utf-8'))
         
        
def checkCommandValidation(commad, data):
    if(commad == "USER" and data != "@"): return True
    if(commad == "PASS" and data != "@"): return True
    if(commad == "PWD" and data == "@"): return True
    if(commad == "MKD" and data != "@"): return True
    if(commad == "MKD-i" and data != "@"): return True
    if(commad == "RMD" and data != "@"): return True
    if(commad == "RMD-f" and data != "@"): return True
    if(commad == "LIST" and data == "@"): return True
    if(commad == "CWD"): return True
    if(commad == "DL" and data != "@"): return True
    if(commad == "HELP" and data == "@"): return True
    if(commad == "QUIT" and data == "@"): return True
    return False
#
###-------------main-----------### 
config = {}
with open('config.json', 'r') as file:
    config = json.load(file)
logFile = createLogFile()
commandPort = config['commandChannelPort']
dataPort = config['dataChannelPort']

commandSocket = socket(AF_INET, SOCK_STREAM)
commandSocket.bind(("",commandPort))
commandSocket.listen(5)
dataSocket = socket(AF_INET, SOCK_STREAM)
dataSocket.bind(("",dataPort))
dataSocket.listen(5)

serverDirectory = os.getcwd()
while True:
    clientCommandSocket,a = commandSocket.accept()
    clientDataSocket,a = dataSocket.accept()

    print("Recieved connection from" , a)
    _thread.start_new_thread(serveClient, (clientCommandSocket,clientDataSocket))
 
commandSocket.close()
dataSocket.close()