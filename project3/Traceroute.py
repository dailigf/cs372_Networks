"""
Author: Francis C. Dailig
Name: Project3 - Traceroute.py
Date: 17 May 2020
Sources:
    Formatting - https://pyformat.info
    Encoding - https://www.programiz.com/python-programming/methods/string/encode
    Raw Sockets - https://sock-raw.org/papers/sock_raw
    struct.pack - https://docs.python.org/2/library/struct.html
    Creating packets - https://stackoverflow.com/questions/40795812/python-icmp-packets-in-raw-sockets
"""
# Adapted from companion material available for the textbook Computer Networking: A Top-Down Approach, 6th Edition
# Kurose & Ross ©2013

from socket import *
import os
import sys
import struct
import time
import select
import binascii

ICMP_ECHO_REQUEST = 8
MAX_HOPS = 30
TIMEOUT  = 2.0
TRIES    = 2

def checksum(string):
    csum = 0
    countTo = (len(string) // 2) * 2

    count = 0
    while count < countTo:
        thisVal = ord(string[count+1]) * 256 + ord(string[count])
        csum = csum + thisVal
        csum = csum & 0xffffffff
        count = count + 2

    if countTo < len(string):
        csum = csum + ord(string[len(string) - 1])
        csum = csum & 0xffffffff

    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    answer = ~csum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer

def build_packet(data_size):
    # First, make the header of the packet, then append the checksum to the header,
    # then finally append the data
    Type = ICMP_ECHO_REQUEST
    Code = 0
    Checksum = 0
    ID = 31337
    Sequence = 1

    Type2 = struct.pack('!b', Type)     #Create Type, 1-byte, Network format, Big-Endian
    Code2 = struct.pack('!b', Code)     #Create Code 1- byte, Netowrk format, Big-Endian
    Checktest2 = struct.pack('!H', Checksum)  #Create filler checksum, 2-bytes, Network Format, Big-Endian
    ID2 = struct.pack('!H', ID)         #Create ID, 2-Bytes, Network Fromat, Big-Endian
    Sequence2 = struct.pack('!h', Sequence) #Create Sequence, 2-Bytes, Network Format, Big Endian
    packet2 = Type2 + Code2 + Checktest2 + ID2 + Sequence2 #Create Packet
    
    data2 = "deadcode"      #dummy data
    data2_as_bytes = data2.encode()  #convert to byte format

    padding = "A" * (data_size - len(data2))
    padding_as_bytes = padding.encode() #convert to raw bytes


    packet2decoded = packet2.decode()
    checkthist2 = packet2decoded + data2 + padding
    Checksum2 = checksum(checkthist2)
    Check = struct.pack('!H', Checksum2)
    packet2 = Type2 + Code2 + Check + ID2 + Sequence2
    packet2 = packet2 + data2_as_bytes + padding_as_bytes

    #padding = b'\x90' * (data_size - len(header) - len(data_as_bytes))
    return packet2



    # Don’t send the packet yet, just return the final packet in this function.
    # So the function ending should look like this
    # Note: padding = bytes(data_size)
    #packet = header + data + padding
    #return packet

def get_route(hostname,data_size):
    print('traceroute to host: {}'.format(hostname))
    #create dictionary for error messages
    errors = {0:'Net is unreachable', 1:'Host is unreachable', 2:'Protocol is unreachable', 3:'Port is unreachable', 4:'Fragmentation is needed and Dont Fragment was set',
            5:'Source route failed', 6:'Destination network is unknown', 7:'Destination host is unknown', 8:'Source host is isolated', 9:'Communcation with dst network is prohibited',
            10:'Communication with dst host is prohibited', 11:'Dst network is unreachable for type of service', 12:'Dst host is unreachable for type of service',
            13:'Communication is prohibted', 14:'Host precedence violation', 15:'Precedence cutoff is in effect'}
    timeLeft = TIMEOUT
    rtt_List = []
    lost_packets = 0
    acked_packet = 0
    loss_rate = 0.0
    for ttl in range(1,MAX_HOPS):
        for tries in range(TRIES):
            destAddr = gethostbyname(hostname)

            # SOCK_RAW is a powerful socket type. For more details:   http://sock-raw.org/papers/sock_raw
            #Fill in start
            mySocket = socket(AF_INET, SOCK_RAW, IPPROTO_ICMP)
            # Make a raw socket named mySocket
            #Fill in end
            # setsockopt method is used to set the time-to-live field.
            mySocket.setsockopt(IPPROTO_IP, IP_TTL, struct.pack('I', ttl))
            mySocket.settimeout(TIMEOUT)
            try:
                d = build_packet(data_size)
                mySocket.sendto(d, (hostname, 0))
                t= time.time()
                startedSelect = time.time()
                whatReady = select.select([mySocket], [], [], timeLeft)
                howLongInSelect = (time.time() - startedSelect)
                lost_packets += 1
                loss_rate = lost_packets / (lost_packets + acked_packet) * 100
                print("  *        *        *    Request timed out.      Loss Rate: %3.2f" %( loss_rate))
               # print("  *        *        *    Request timed out. test")
                recvPacket, addr = mySocket.recvfrom(1024)
                timeReceived = time.time()
                timeLeft = timeLeft - howLongInSelect
                if timeLeft <= 0:
                    lost_packets += 1
                    loss_rate = lost_packets / (lost_packets + acked_packet) * 100
                    print("  *        *        *    Request timed out.      Loss Rate: %3.2f" %(loss_rate))

            except timeout:
                continue

            else:
                #Fill in start

                header = recvPacket[20:28]
                types, code, checksum, ID, sequence = struct.unpack("bbHHh", header)
                #Fetch the icmp type from the IP packet
                #Fill in end

                if types == 11:
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
                    rtt = (timeReceived - t)*1000
                    rtt_List.append(rtt)
                    acked_packet += 1
                    loss_rate = lost_packets / (lost_packets + acked_packet) * 100
                    print("  %d    rtt=%.0f ms      min_rtt=%.0f ms     max_rtt=%.0f ms     avg_rtt=%.0f ms     Loss Rate: %3.2f       %s" 
                            %(ttl, (timeReceived -t)*1000, min(rtt_List), max(rtt_List), sum(rtt_List)/len(rtt_List), loss_rate, addr[0]))

                elif types == 3:
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
                    #print("  %d    rtt=%.0f ms    %s" %(ttl, (timeReceived-t)*1000, addr[0]))
                    rtt = (timeReceived - t)*1000
                    rtt_List.append(rtt)
                    acked_packet += 1
                    loss_rate = lost_packets / (lost_packets + acked_packet) * 100
                    print("  %d    rtt=%.0f ms      min_rtt=%.0f ms     max_rtt=%.0f ms     avg_rtt=%.0f ms     Loss Rate: %3.2f        %s" 
                            %(ttl, (timeReceived -t)*1000, min(rtt_List), max(rtt_List), sum(rtt_List)/len(rtt_List), loss_rate, addr[0]))

                elif types == 0:
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
                    #print("  %d    rtt=%.0f ms    %s" %(ttl, (timeReceived - timeSent)*1000, addr[0]))
                    rtt = (timeReceived - t)*1000
                    rtt_List.append(rtt)
                    acked_packet += 1
                    loss_rate = lost_packets / (lost_packets + acked_packet) * 100
                    print("  %d    rtt=%.0f ms      min_rtt=%.0f ms     max_rtt=%.0f ms     avg_rtt=%.0f ms     Loss Rate: %3.2f        %s" 
                            %(ttl, (timeReceived -t)*1000, min(rtt_List), max(rtt_List), sum(rtt_List)/len(rtt_List), loss_rate, addr[0]))
                    return

                else:
                    #print error code and message
                    print("Error.   Code: {}.   Message: {}".format(code, errors.get(code)))
                break
            finally:
                mySocket.close()


print('Argument List: {0}'.format(str(sys.argv)))

data_size = 0
if len(sys.argv) >= 2:
    data_size = int(sys.argv[1])

get_route("oregonstate.edu",data_size)
#get_route("gaia.cs.umass.edu",data_size)
#get_route("koreaherald.com", data_size)
#get_route("eng.koreabaseball.com", data_size)
#get_route("usna.edu", data_size)
