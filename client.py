import socket
import struct
from threading import Thread
from scapy.arch import get_if_addr

UDP_IP = '127.0.0.1'
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


def send_to_server(sock, inputMessage):
    data = input(inputMessage+"\n")
    sock.sendall(data.encode())


"""
sets UDP socket 
"""



def main():
    print("Client started, listening for offer requests...")  # waits for server suggestion
    UDPsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # init UDP socket
    UDPsock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    UDPsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    UDPsock.bind((UDP_IP,UDP_PORT))
    time.sleep(0.1)
    data, address = UDPsock.recvfrom(12) # getting data andd adress from the server message
    print(data)
    serverIP = str(address[0])
    try:
        magicCookie, message_type, server_tcp_port = struct.unpack('LBH', data)  # get message in specific format
        print(str(server_tcp_port))
        if magicCookie == 0xabcddcba or message_type == 0x2:  # check if message is as expected
            print("Received offer from " + serverIP + ", attempting to connect...")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # init TCP socket
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            sock.connect((serverIP, server_tcp_port))
            send_to_server(sock, "Enter your team's name: ")  # send team's name to server
            get_from_server(sock)  # the game begin message
            ansThread = Thread(target=send_to_server,args=(sock,"",),daemon=True)
            ansThread.start()
            get_from_server(sock)  # the game end message
            sock.close()
        else:
            print("Bad UDP Message Format")  # got message not in the expected format
    except Exception as e:
        print(e)
        UDPsock.close()


if __name__ == "__main__":
    main()
