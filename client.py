# Student name: Michael Hrenko
# Student OSU ID: 934396070
# Course: CS 372
# Programming Project: Client-Server Chat

# #################################################################################################################### #
# Sources                                                                                                              #
#                                                                                                                      #
# #################################################################################################################### #

# "Computer Networking: A Top-down Approach", 7th edition by James Kurose and Keith Ross, Section 2.71 - "TCPClient.py"
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
# clientChat                                                                                                           #
#                                                                                                                      #
# Description:                                                                                                         #
# Runs the client side of the chat with the server.                                                                    #
#                                                                                                                      #
# My approach:                                                                                                         #
# (1) Initialize (a) a connection to the server using the same host and port and (b) a send message thread.            #
#   -  Threading is used because we need the ability to send and receive multiple messages. To accommodate this,       #
#      each send and receive function needs to remain open at the same time. This can best be done using               #
#      parallelism.                                                                                                    #
# (2) Call receive message in the main function.                                                                       #
#   - Both the send and receive functions are while loops that continue to run while the client and server             #
#     connections are open.                                                                                            #
# (3) The programs ends when the client enters '/q' (stopping the thread), or the server quits and the receive         #
#       message detects this.                                                                                          #                                                                                                       #
#   - Neither the client nor the server send a quit message.                                                           #
#                                                                                                                      #
# #################################################################################################################### #
class clientChat:

    # ################################################################################################################ #
    # __init__()                                                                                                       #
    #                                                                                                                  #
    # ################################################################################################################ #
    def __init__(self):

        self.host = 'localhost'
        self.port = 15777
        self.clientSocket = None
        self.clientAddress = None
        self.threadSend = None
        self.connected = False

    # ################################################################################################################ #
    # sendMessage()                                                                                                    #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # (1) Receives a message input by the client.                                                                      #
    # (2) If the message is 'q', calls closeChat() to stops the thread.                                                #
    # (3) Else tries to send the message to the server. If the server closed the connection, sets                      #
    #   self.connected to False to indicate that receiveMessage() should also stop.                                    #
    #                                                                                                                  #
    # Notes:                                                                                                           #
    # Remains active while client and server are still connected.                                                      #
    #                                                                                                                  #
    # ################################################################################################################ #
    def sendMessage(self):

        while self.connected:

            # Get the message from the user.
            clientMessage = (input()).strip()

            # '/q' quits the program by calling closeChat() and setting self.connected to False 
            #   so receiveMessage() also stops.
            if clientMessage == "/q":
                self.connected = False
                self.closeChat()
            else:
                # Use a try function b/c the server may have closed the connection.
                # If that occurs call closeChat() and set self.connected to False so 
                #   receiveMessage() also stops. 
                try:
                    self.clientSocket.send(clientMessage.encode('utf-8'))           
                except:
                    self.connected = False
                    self.closeChat()

    # ################################################################################################################ #
    # receiveMessage()                                                                                                 #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Receives and prints messages from the server.                                                                    #
    #                                                                                                                  #  
    # Notes:                                                                                                           #
    # Remains active while client and server are still connected.                                                      #
    #                                                                                                                  #
    # ################################################################################################################ #
    def receiveMessage(self):
        while self.connected:

            # Use a try function b/c the server may have closed the connection before this was able to run.
            #  If that happens, break the loop. 
            try:
                # Receive data from the server socket as a bytes object.
                # 1024 is the size of the buffer
                serverMessage = self.clientSocket.recv(1024).decode('utf-8')
                print(f"Server: {serverMessage}")
            
            except:
                self.connected = False
                break

    # ################################################################################################################ #
    # connect()                                                                                                        #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # (1) Connects to the client socket.                                                                               #
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
            self.clientSocket = socket(AF_INET, SOCK_STREAM)

            # Initiate the TCP connection (aka the three-way handshake) between the client 
            #   and server (at the server address and port above);
            self.clientSocket.connect((self.host, self.port))
            print(f"\nConnected to {self.host} on port {self.port}")
            print("Enter a message or /q to quit")

            self.connected = True

            # Initialize and start threading the sendMessage function.
            self.threadSend = threading.Thread(target=self.sendMessage, daemon=True)
            self.threadSend.start()

        except:
           print("Cannot connect to server") 

    # ################################################################################################################ #
    # closeChat()                                                                                                      #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Closes the client socket.                                                                                         #
    #                                                                                                                  #
    # ################################################################################################################ #
    def closeChat(self):

        self.clientSocket.close()

# #################################################################################################################### #
# Run program                                                                                                          #
#                                                                                                                      #
# #################################################################################################################### #
if __name__ == '__main__':

    chat = clientChat()
    chat.connect()
    chat.receiveMessage()