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
TCP_PORT = 21329
MESSAGE_LENGTH = 1024
TIME_TO_CONNECT = 10  # seconds
TIME_TO_PLAY = 10  # seconds
MAX_CONNECTIONS_TO_SERVER = 2
COLORS = ['\033[95m','\033[94m','\033[96m','\033[92m','\033[93m','\033[91m']
participants = {}
currentParticipants = {}

def randColor():
    num = randrange(5)
    return COLORS[num]

def make_bytes_message():
    return struct.pack('IBH', 0xabcddcba, 0x2, TCP_PORT)
    # support  - L unsigned long
    # B - unsigned char
    # H - unsigned short


def send_broadcast(clients):
    message = randColor()+"Server started, listening on IP address " + ip_address
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP need to check ipproto
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  # allow server to send broadcasts
    print(message)
    while len(clients) < MAX_CONNECTIONS_TO_SERVER:
        send_bytes = make_bytes_message()
        sock.sendto(send_bytes, (UDP_IP, UDP_PORT))  # check udp_ip
        time.sleep(1)  # wait 1 sec
    sock.close()


def connect_clients(clients, sock):
    while len(clients) < MAX_CONNECTIONS_TO_SERVER:
        try:
            print("start connect")
            clientSocket, clientAdress = sock.accept()
            print("\nhi\n")
            clients.append(clientSocket)
            if clientAdress not in participants.keys():
                participants[clientAdress] = 0
                currentParticipants[clientSocket] = clientAdress
        except:
            print(randColor()+"error occured during connect client")



def generate_question(firstName, secondName):
    squered = randrange(1,3)
    normalx = randrange(1,3)
    nonX = randrange(1,9)
    ans = str(squered*2 + normalx)
    squered = str(squered) + "x^2"
    normalx = str(normalx) + "x"
    message = randColor()+"Welcome to Quick Maths.\n"
    message += randColor()+"Player 1: " + firstName + '\n'
    message += randColor()+"Player 2: " + secondName + '\n'
    message += randColor()+"==\n"
    message += randColor()+"Please answer the following question as fast as you can:\n"
    message += randColor()+"How much is f'(1) of " + squered + "+" + normalx +"+" + str(nonX) + "?\n"
    return message, ans


def send_message(message, conA, conB):
    message = message.encode()
    conA.sendall(message)
    conB.sendall(message)


def generate_end_message(winner, ans):
    finish_game_message = randColor()+"Game over!\nThe correct answer was " + ans + "!\n"
    winner_message = finish_game_message +randColor()+ "Congratulations to the winner: " + winner + "\n"
    draw_message = finish_game_message +randColor()+ "The game ended with a draw\n"
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
    secondClientName = clients[1].recv(MESSAGE_LENGTH).decode()
    clientsDictionary = {clients[0]: firstClientName, clients[1]: secondClientName, "": ""}
    message, ans = generate_question(firstClientName, secondClientName)  # generate the question and return is answear
    send_message(message, clients[0], clients[1])  # send
    clientAnswer, answerClientSocket = collect_data(clientsDictionary)
    clientAnswerName = clientsDictionary[answerClientSocket]
    nonAnswerClientName = firstClientName if clientAnswerName != firstClientName else secondClientName
    winner = "" if clientAnswer == "" else clientAnswerName if clientAnswer == ans else nonAnswerClientName
    if winner != "":
        for cSocket in clientsDictionary:
            if clientsDictionary[cSocket] == winner:
                winnerAddress = currentParticipants[cSocket]
        participants[winnerAddress] = participants[winnerAddress] + 1
    end_message = generate_end_message(winner, ans)  # generate end message
    send_message(end_message, clients[0], clients[1])


def closeSockets(clients):
    for sock in clients:
        sock.close()

def printStatistics():
    statistics = randColor() + "statics:\n"
    for adres in participants.keys():
        statistics += randColor() + str(adres) +" won "+ str(participants[adres]) + " times\n"
    print(statistics)
    

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:  # init the TCP socket
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)  # allow use 2 sockets from the same port
        sock.bind(('', TCP_PORT))  # bind the socket with our port
        sock.listen()  # set queue of waiting size to num of connections -1
        while True:
            try:
                clients = list()  # client list
                client_connector = Thread(target=connect_clients, args=(clients, sock,))  # accepts new players
                client_connector.start()
                send_broadcast(clients)
                client_connector.join()
                time.sleep(TIME_TO_CONNECT)  # waits 10 seconds after assign 2nd user
                start_game(clients)  # play the game
                closeSockets(clients)
                print(randColor()+"Game over, sending out offer requests...")
                currentParticipants.clear()
                printStatistics()
            except:
                print(randColor()+"error occured, game stopped")
                break

if __name__ == "__main__":
    main()
