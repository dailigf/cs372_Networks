#!/usr/bin/env python3
"""
Author: Francis C. Dailig
Project Name:  Project 1
Description:  Code for Project 1.  Three test cases: 1 - Small HTTP object; 2 - Large HTTP object; 3 - Simple HTTP Server
"""

import argparse
import socket


def testCase1():
    """
    This function will run the first test case for project 1
    It will request a small http object from gaia.cs.umass.edu
    Source used:  https://stackoverflow.com/questions/49848375/how-to-use-python-socket-to-get-a-html-page
    """

    #Create socket and connect to webserver
    host = "gaia.cs.umass.edu"  #human readable address of the webserver
    port = 80                   #port of the webserver
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Create TCP Socket
    s.connect((host,port))      #connect to the Webserver

    #Send Request for http object
    request = "GET /wireshark-labs/INTRO-wireshark-file1.html HTTP/1.1\r\nHost:gaia.cs.umass.edu\r\n\r\n"
    s.send(request.encode())

    #Get Response
    response = s.recv(1024)
    http_response = repr(response)

    #close socket
    s.close()

    #Print Response
    print('Request: {}'.format(request))
    print('[RECV] - {}\n'.format(len(response)))
    print(response.decode())

def testCase2():
    """
    This function will run test case 2 of project 1
    This will request a large html object
    Source use:  https://steelkiwi.com/blog/working-tcp-sockets/
    """

    #Create socket and connect to webserver
    host = "gaia.cs.umass.edu"  #human readable address of the webserver
    port = 80                   #port of the webserver
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Create TCP Socket
    s.connect((host,port))      #connect to the Webserver

    #Send Request to web server
    request = "GET /wireshark-labs/HTTP-wireshark-file3.html HTTP/1.1\r\nHost:gaia.cs.umass.edu\r\n\r\n"
    s.send(request.encode())
    chunk = s.recv(1024)
    response = chunk
    while True:
            chunk = s.recv(1024)
            response += chunk
            if not chunk:
                    break
    
    print('Request: {}'.format(request))
    print('[RECV] - {}'.format(len(response)))
    print(response.decode())
    s.close()

def testCase3():
    """
    This function will run test case 3 of project 1
    This will create simple http server on port 31337
    Source used: https://stackoverflow.com/questions/39535855/send-receive-data-over-a-socket-python3
    """

    server_addr = ('0.0.0.0',31337) #server will listen on port 31337

    data = "HTTP/1.1 200 OK\r\n"\
                    "Content-Type: text/html; charset=UTF-8\r\n\r\n"\
                    "<html>Congratulations! You've downloaded the first Wireshark lab file!</html>\r\n"
    
    #Create a socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    #Bind address
    sock.bind(server_addr)
    
    #Listen for incomming connection
    sock.listen(5)
    print("Webserver is listening.  Browse to: http://127.0.0.1:31337")
    while True:
        c, addr = sock.accept()
        received = c.recv(1024)
        print("Received: {}".format(received))
        print("sending >>>>>>>>>>>>>>>>>>>>")
        print(data)
        print("<<<<<<<<<<<<<<<<<<<<")
        c.send(bytes(data, 'utf8'))
        c.close()
        break

def main():
    parser = argparse.ArgumentParser(usage='python3 http.py -case {1, 2, 3}', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-case', required=True, choices=range(1,4), type=int,
            help="test case number:\n1 - small http file\n2 - large http file\n3 - http server\n")
    args = parser.parse_args()
    
    if args.case == 1:
        print("Running test Case 1 - Small HTTP Request")
        testCase1()
    elif args.case == 2:
        print("Running test case 2 - Large HTTP Request.")
        testCase2()
    else: 
        print("Runnning test case 3 - Simple HTTP Server.")
        testCase3()
    
if __name__ == "__main__":
    main()
