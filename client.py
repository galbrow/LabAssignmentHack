import os
import socket
import struct
import sys
import time
from threading import Thread
import getch
import signal
from scapy.arch import get_if_addr

UDP_PORT = 13117
MESSAGE_LENGTH = 1024
TIME_TO_PLAY = 10  # seconds

"""
gets messages from the server over TCP
"""
def get_from_server(sock):
        print(sock.recv(MESSAGE_LENGTH).decode())
 
"""
sends messages to the server over TCP
"""
def send_to_server(sock, message):
        sock.sendall(message.encode())
    
"""
sets UDP socket 
"""
def setUDPSocket():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # init UDP socket
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", UDP_PORT))
    return sock


def main():
    print("Client started, listening for offer requests...")  # waits for server suggestion
    UDPsock = setUDPSocket()
    TCPsock = acceptOffer(UDPsock.recvfrom(MESSAGE_LENGTH))
    data, address = sock.recvfrom(MESSAGE_LENGTH) # getting data andd adress from the server message
    serverIP = str(address[0])
    try:
        magicCookie, message_type, server_tcp_port = struct.unpack('LBH', data)  # get message in specific format
        if magicCookie == 0xabcddcba or message_type == 0x2:  # check if message is as expected
            print("Received offer from " + serverIP + ", attempting to connect...")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # init TCP socket
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            sock.connect((serverIP, server_tcp_port))
            name = input("Enter your team's name: ")
            send_to_server(sock, name)  # send team's name to server
            get_from_server(sock) # the game begin message
            answer = input()
            send_to_server(sock, answer)
            get_from_server(sock) # the game end message
            while True:
                try:
                    ch = getch.getch().encode()  # blocking, wait for char
                    sock.sendall(ch)  # if socket is still open, send it
                except:
                    break
        else:
            print("Bad UDP Message Format")  # got message not in the expected format
    except:
        pass


if __name__ == "__main__":
    main()