#!/usr/bin/env python3
"""
Author: Francis C. Dailig
Project Name:  Project 4 - Chat Server
Source: https://www.youtube.com/watch?v=Lbfe3-v7yE0
"""

import argparse
import socket
import re

#Length of the HEader that will be prefixed to each msg, it will hold the length of the msg payload
HEADER_LENGTH = 15
#size of chunks to receive during each recv() call
CHUNK_LENGTH = 512


def startChatting(s):
    """
    This is the chatting function, it will send a welcome message first.  Then it will recv a message from the client and then send the server's message; repeat
    """

    #create regex for quitting
    pattern = "/q"


    #server welcome message
    welcome = "Welcome to the chat program.\nType /q to quit\nEnter message to send..."
    #get length of the of the welcome message, format it, this will be the header of the message to send
    msg_len = f'{len(welcome):<{HEADER_LENGTH}}'
    #msg to send will have a header with the length of the message followed by the message
    msg = msg_len + welcome
 
    #accept incoming conection then send the welcome message
    c, addr = s.accept()
    c.send(bytes(msg, 'utf-8'))
    
    msg_rcvd_buffer = ""    #recv buffer for incoming message
    msg_rcvd = ""           #this will hold the whole incoming message

    #while loop, will exit if user enters '/q'
    while re.search(pattern, msg_rcvd) == None:
        msg_rcvd_buffer = c.recv(CHUNK_LENGTH).decode()
        #Get the header of the received msg
        rcvd_len = int(msg_rcvd_buffer[:HEADER_LENGTH])
        msg_rcvd = msg_rcvd_buffer[HEADER_LENGTH:]

        if re.search(pattern, msg_rcvd):
            break

        #enter to while loop keep collecting chunks until whole message is received.
        while len(msg_rcvd) < rcvd_len:
            msg_rcvd_buffer = c.recv(CHUNK_LENGTH)
            msg_rcvd += msg_rcvd_buffer

        #display message received from user
        print(msg_rcvd)
        msg_to_send = input(">>> ")
        msg_len = f'{len(msg_to_send):<{HEADER_LENGTH}}'
        msg_to_send = msg_len + msg_to_send
        
        c.send(bytes(msg_to_send, 'utf8'))


def main():
    parser = argparse.ArgumentParser(usage='python3 server -p <port number>', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-p', required=True, type=int)
    args = parser.parse_args()
    
    print('server is running on port {}'.format(args.p))
    print('To connect:\npython3 client.py -i 127.0.0.1 -p {}'.format(args.p))

    #Create socket
    server_addr = ('0.0.0.0', args.p)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(server_addr)
    sock.listen(1)
    startChatting(sock)
    sock.close()
    
if __name__ == "__main__":
    main()
