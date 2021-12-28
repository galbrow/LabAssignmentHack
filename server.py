import socket
import time
import struct
from queue import Queue
from threading import Thread
from scapy.all import get_if_addr
from random import randrange

ip_address = get_if_addr("eth1")
UDP_IP = '127.0.0.1'
UDP_PORT = 13117
TCP_PORT = 2132
MESSAGE_LENGTH = 1024
TIME_TO_CONNECT = 10  # seconds
TIME_TO_PLAY = 10  # seconds
MAX_CONNECTIONS_TO_SERVER = 2


def make_bytes_message():
    return struct.pack('LBH', 0xabcddcba, 0x2, TCP_PORT)
    # support  - L unsigned long
    # B - unsigned char
    # H - unsigned short


def send_broadcast(clients):
    message = "Server started, listening on IP address " + ip_address
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP need to check ipproto
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  # allow server to send broadcasts
    sock.bind((UDP_IP, UDP_PORT))
    print(message)
    while len(clients) < 2:
        send_bytes = make_bytes_message()
        sock.sendto(send_bytes, (UDP_IP, UDP_PORT))  # check udp_ip
        time.sleep(1)  # wait 1 sec
    sock.close()


def connect_clients(clients, sock):
    while len(clients) < 2:
        try:
            print("strating conncet a client")
            clientSocket, clientAdress = sock.accept()
            print("connected to:\nclient addr[0] --> " + str(clientAdress[0]) + "\nclient addr[1] --> " + str(clientAdress[1]))
            clients.append(clientSocket)
        except Exception as e:
            print(e)


def generate_question(firstName, secondName):
    leftOperand = randrange(4)
    rightOperand = randrange(4)
    ans = str(leftOperand + rightOperand)
    leftOperand = str(leftOperand)
    rightOperand = str(rightOperand)
    message = "Welcome to Quick Maths.\n"
    message += "Player 1: " + firstName + '\n'
    message += "Player 2: " + secondName + '\n'
    message += "==\n"
    message += "Please answer the following question as fast as you can:\n"
    message += "How much is " + leftOperand + "+" + rightOperand + "?\n"
    return message, ans


def send_message(message, conA, conB):
    message = message.encode()
    conA.sendall(message)
    conB.sendall(message)


def generate_end_message(winner, ans):
    finish_game_message = "Game over!\nThe correct answer was " + ans + "!\n"
    winner_message = finish_game_message + "Congratulations to the winner: " + winner + "\n"
    draw_message = finish_game_message + "The game ended with a draw\n"
    return draw_message if winner == "" else winner_message


def collect_data_from_client(client, q):
    ans = client.recv(MESSAGE_LENGTH).decode()
    q.put((ans, client))


def collect_data(clients):
    q = Queue()
    while q.empty():
        cls = list()
        for clientSocket in clients.keys():  # make a list of a clients thread
            if clientSocket != "":
                clThread = Thread(target=(collect_data_from_client), args=(clientSocket, q,))
                cls.append(clThread)
        for th in cls:  # begin all threads in paralel
            th.start()
        try:
            return q.get(True, TIME_TO_PLAY)
        except:
            return "", ""

def start_game(clients):
    firstClientName = clients[0].recv(MESSAGE_LENGTH).decode()
    print(firstClientName)
    secondClientName = clients[1].recv(MESSAGE_LENGTH).decode()
    print(secondClientName)
    clientsDictionary = {clients[0]: firstClientName, clients[1]: secondClientName, "": ""}
    message, ans = generate_question(firstClientName, secondClientName)  # generate the question and return is answear
    send_message(message, clients[0], clients[1])  # send
    print(message)
    clientAnswer, answerClientSocket = collect_data(clientsDictionary)
    clientAnswerName = clientsDictionary[answerClientSocket]
    nonAnswerClientName = firstClientName if clientAnswerName != firstClientName else secondClientName
    winner = "" if clientAnswer == "" else clientAnswerName if clientAnswer == ans else nonAnswerClientName
    end_message = generate_end_message(winner, ans)  # generate end message
    print(end_message)
    send_message(end_message, clients[0], clients[1])


def closeSockets(clients):
    for sock in clients:
        sock.close()


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:  # init the TCP socket
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)  # allow use 2 sockets from the same port
        sock.bind(("", TCP_PORT))  # bind the socket with our port
        sock.listen()  # set queue of waiting size to num of connections -1
        while True:
            try:
                clients = list()  # client list
                client_connector = Thread(target=connect_clients, args=(clients, sock,))  # accepts new players
                client_connector.start()
                send_broadcast(clients)
                client_connector.join()
                time.sleep(1)  # waits 10 seconds after assign 2nd user
                start_game(clients)  # play the game
                closeSockets(clients)
                print("Game over, sending out offer requests...")
            except Exception as e:
                print("-----------------")
                print(e)
                print("-----------------")
                break
    print("done")

if __name__ == "__main__":
    main()
