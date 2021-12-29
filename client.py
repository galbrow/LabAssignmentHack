import socket
import struct
from threading import Thread
from scapy.arch import get_if_addr

UDP_IP = '127.0.0.1'
UDP_PORT = 13117
MESSAGE_LENGTH = 1024
TIME_TO_PLAY = 10  # seconds
COLORS = ['\033[95m','\033[94m','\033[96m','\033[92m','\033[93m','\033[91m']


"""
gets messages from the server over TCP
"""


def get_from_server(sock):
    print(sock.recv(MESSAGE_LENGTH).decode())


"""
sends messages to the server over TCP
"""


def send_to_server(sock, inputMessage):
    data = input(COLORS[0]+inputMessage+"\n")
    sock.sendall(data.encode())


def threadToKill(sock):
    ansThread = Thread(target=send_to_server, args=(sock, "",), daemon=True)
    ansThread.start()
    get_from_server(sock)  # the game end message
    sock.close()


def main():
    print(COLORS[1]+"Client started, listening for offer requests...")  # waits for server suggestion
    UDPsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # init UDP socket
    UDPsock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    UDPsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    UDPsock.bind((UDP_IP,UDP_PORT))
    data, address = UDPsock.recvfrom(12) # getting data andd adress from the server message
    serverIP = str(address[0])
    while True:
        try:
            magicCookie, message_type, server_tcp_port = struct.unpack('IBH', data)  # get message in specific format
            print(str(server_tcp_port))
            if magicCookie == 0xabcddcba or message_type == 0x2:  # check if message is as expected
                print(COLORS[2]+"Received offer from " + serverIP + ", attempting to connect...")
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # init TCP socket
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.connect((serverIP, server_tcp_port))
                send_to_server(sock, "Enter your team's name: ")  # send team's name to server
                get_from_server(sock)  # the game begin message
                th = Thread(target=threadToKill, args=(sock,))
                th.start()
                th.join()
            else:
                print(COLORS[3]+"Bad UDP Message Format")  # got message not in the expected format
        except Exception as e:
            UDPsock.close()


if __name__ == "__main__":
    main()
