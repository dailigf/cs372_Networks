#!/usr/bin/env python3
"""
Author: Francis C. Dailig
Project Name:  Project 4 - Chat program
Description:  Code for the client of the chat program
"""

import argparse
import socket


#Established the length of the header that will contain the length of the payload
HEADER_LENGTH = 15
#Chunk Length is the amount of the data to receive each time recv() function is called
#This should never be less than the HEADER_LENGTH
CHUNK_LENGTH = 512



def startChatting(s):
    """
    chatting function.  It will receive a message from the server, display it, then receive a message from the client to send to the server; repeat.
    """

    #Listen for incomming connection
    while True:
        #variable for the entire received message: msg header + msg payload
        msg_rcvd = ""
        #variable to hold the length of msg payload
        msg_len = -5


        msg_rcvd = s.recv(CHUNK_LENGTH)
        if msg_rcvd:
            #get the length of the msg payload
            msg_len = int(msg_rcvd[:HEADER_LENGTH])
        else:
            break

        msg = msg_rcvd[HEADER_LENGTH:].decode()
        #while loop will continue receiving mesg chunks until entrie message is received
        while len(msg) < msg_len:
            msg_rcvd = s.recv(5).decode("utf-8")
            msg += msg_rcvd

        print(msg)

        #Get message to send from the user
        msg_to_send = input(">>> ")
        msg_to_send_length = f'{len(msg_to_send):<{HEADER_LENGTH}}'
        msg_to_send = msg_to_send_length + msg_to_send
        s.send(bytes(msg_to_send, 'utf-8'))




def main():
    parser = argparse.ArgumentParser(usage='python3 client.py -h <ip address>  -p <port number>', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-i', required=True, type=str)
    parser.add_argument('-p', required=True, type=int)
    args = parser.parse_args()

    #get ip address
    host = socket.gethostbyname(args.i)

    server_addr = (host, args.p)

    #establish connection to the server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(server_addr)

    #Start the chatting function
    startChatting(s)
    #close the connection
    s.close()
    
    
if __name__ == "__main__":
    main()
