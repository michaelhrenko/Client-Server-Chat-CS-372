# Student name: Michael Hrenko
# Student OSU ID: 934396070
# Course: CS 372
# Programming Project: Client-Server Chat

# #################################################################################################################### #
# Sources                                                                                                              #
#                                                                                                                      #
# #################################################################################################################### #

# "Computer Networking: A Top-down Approach", 7th edition by James Kurose and Keith Ross, Section 2.71 - "TCPServer.py"
# "socket — Low-level networking interface", python.org, https://docs.python.org/3/library/socket.html
# "threading — Thread-based parallelism", python.org, https://docs.python.org/3/library/threading.html
# "An Intro to Threading in Python", Jim Anderson, Real Python, https://realpython.com/intro-to-python-threading/

# #################################################################################################################### #
# Import packages                                                                                                      #
#                                                                                                                      #
# #################################################################################################################### #

# Socket is the python package that provides a "Low-level networking interface" (see source above)
from socket import *

# Threading is the python package that provides parallelism "Low-level networking interface" (see source above)
import threading

# #################################################################################################################### #
# serverChat                                                                                                           #
#                                                                                                                      #
# Description:                                                                                                         #
# Runs the server side of the chat with the client.                                                                    #
#                                                                                                                      #
# My approach:                                                                                                         #
# (1) Initialize (a) the bind for the server, (b) listening for a connection from the client, (c) a send               #
#     message thread.                                                                                                  #
#   -  Threading is used because we need the ability to send and receive multiple messages. To accommodate this,       #
#      each send and receive function needs to remain open at the same time. This can best be done using               #
#      parallelism.                                                                                                    #
# (2) Call receive message in the main function.                                                                       #
#   - Both the send and receive functions are while loops that continue to run while the client and server             #
#     connections are open.                                                                                            #
# (3) The program ends when the server enters '/q' (stopping the thread), or the client quits and the receive          #
#       message detects this.                                                                                          #                                                                                                       #
#   - Neither the client nor the server send a quit message.                                                           #
#                                                                                                                      #
# #################################################################################################################### #

class serverChat:

    # ################################################################################################################ #
    # __init__()                                                                                                       #
    #                                                                                                                  #
    # ################################################################################################################ #
    def __init__(self):

        self.host = 'localhost'
        self.port = 15777
        self.clientSocket = None
        self.clientAddress = None
        self.serverSocket = None
        self.threadSend = None
        self.connected = False
        self.clientMessageCount = 0

    # ################################################################################################################ #
    # sendMessage()                                                                                                    #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # (1) Receives a message input by the server.                                                                      #
    # (2) If the message is 'q', calls closeChat() to stop the thread.                                                 #
    # (3) Else tries to send the message to the client. If the client closed the connection, sets                      #
    #   self.connected to False to indicate that receiveMessage() should also stop.                                    #
    #                                                                                                                  #
    # Notes:                                                                                                           #
    # Remains active while client and server are still connected.                                                      #
    #                                                                                                                  #
    # ################################################################################################################ #
    def sendMessage(self):

        while self.connected:

            # Get the message from the user.
            serverMessage = (input()).strip()

            # '/q' quits the program by calling closeChat() and setting self.connected to False 
            #   so receiveMessage() also stops.
            if serverMessage == "/q":
                self.connected = False
                self.closeChat()
            else:
                # Use a try function b/c the client may have closed the connection.
                # If that occurs call closeChat() and set self.connected to False so 
                #   receiveMessage() also stops. 
                try:
                    self.clientSocket.send(serverMessage.encode('utf-8'))           
                except:
                    self.connected = False
                    self.closeChat()

    # ################################################################################################################ #
    # receiveMessage()                                                                                                 #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Receives and prints messages from the client.                                                                    #
    #                                                                                                                  #  
    # Notes:                                                                                                           #
    # Remains active while client and server are still connected.                                                      #
    #                                                                                                                  #
    # ################################################################################################################ #
    def receiveMessage(self):
        while self.connected:

            # Use a try function b/c the client may have closed the connection before this was able to run.
            #  If that happens, break the loop. 
            try:
                # Receive data from the client socket as a bytes object.
                # 1024 is the size of the buffer
                clientMessage = self.clientSocket.recv(1024).decode('utf-8')
                print(f"Client: {clientMessage}")

                # This counter is used so receiveMessage can print an intro message (only once) to 
                #   the server user after the first message is received from the client. 
                self.clientMessageCount += 1

                # Print this on the first instance of the client sending a message. 
                if self.clientMessageCount == 1:
                    print("Enter a message or /q to quit")
                    
            except:
                self.connected = False
                break

    # ################################################################################################################ #
    # connect()                                                                                                        #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # (1) Bind the server to the host/port and listens for a connection from the client.                               #
    # (2) Connects to the client socket.                                                                               #
    # (2) Initializes and starts threading for the sendMessage function.                                               #
    #                                                                                                                  #
    # Notes:                                                                                                           #
    # Threading is used because we need the ability to send and receive multiple messages. To accommodate  this,       #
    #   each send and receive function needs to remain open at the same time. This can best be done using              #
    #   parallelism.                                                                                                   #
    #                                                                                                                  #
    # ################################################################################################################ #
    def connect(self):

        try:

            # Create the socket for the client.
            # AF_INET: underlying network is using IPv4.
            # SOCK_STREAM: use the TCP socket. 
            # Use TCP because we're sending/receiving data which needs to be accurate. 
            self.serverSocket = socket(AF_INET, SOCK_STREAM)

            # Set a socket reuse option before binding the server.
            self.serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

            # Bind/set the socket to the address and port above.
            self.serverSocket.bind((self.host, self.port))

            # Initialize server to start listening for connection requests from the client. 
            # 1 sets the maximum number of queued connections.
            self.serverSocket.listen(1)
            print(f"\nServer listening on {self.host} port {self.port}")

            # When the client sends the request, the server will create a new socket for it. 
            # Then the client and server will complete the three-way handshake.
            self.clientSocket, self.clientAddress = self.serverSocket.accept()
            print(f"Connected to {self.clientAddress[0]} on port {self.clientAddress[1]}")
            print("Waiting for message...")

            self.connected = True

            # Initialize and start threading the sendMessage function.
            self.threadSend = threading.Thread(target=self.sendMessage, daemon=True)
            self.threadSend.start()

        except:
           print("Cannot bind server") 

    # ################################################################################################################ #
    # closeChat()                                                                                                      #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # (1) Closes the client socket.                                                                                    #
    # (2) Closes the server socket.                                                                                    #
    #                                                                                                                  #
    # ################################################################################################################ #
    def closeChat(self):
        self.clientSocket.close()
        self.serverSocket.close()

# #################################################################################################################### #
# Run program                                                                                                          #
#                                                                                                                      #
# #################################################################################################################### #
if __name__ == '__main__':

    chat = serverChat()
    chat.connect()
    chat.receiveMessage()
