import socket
import time
import struct
import pickle

import config

BLOCK_SIZE = 15
HEADER_SIZE = 14
MAX_DATA_SIZE = 1456

DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = socket.gethostbyname(socket.gethostname())
FORMAT = 'utf-8'

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = (socket.gethostname(), 1234)

server_socket.bind(server_address)
print(f"[LISTENING] Server is listening on {SERVER}")

def send(msg, address):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER_SIZE - len(send_length))
    server_socket.sendto(send_length, address)
    server_socket.sendto(message, address)

# Note we do not use .listen() because UDP does not listen on connections,
# it right away takes a message from recvfrom
while True:
    message, address = server_socket.recvfrom(MAX_DATA_SIZE)

    if message:

        if pickle.loads(message)[1] == config.signals['CONNECTION_INITIALIZATION']:
            msg = "Hello, and welcome!:)"
            msg = f'{len(msg):<{HEADER_SIZE}}' + msg  # Nastavi fixny header size a za to doplni tu msg
            send(msg, address)

        print(f"Printing header: {pickle.loads(message)[1]}")

    else:
        pass

    # Prva sprava nam da vediet, aku velkost bude mat prichadzajuca sprava a potom prijimeme
    # spravu s velkostou, ktoru sme zistili

    # msg_length, address = server_socket.recvfrom(HEADER_SIZE)
    # msg_length = msg_length.decode(FORMAT)
    #
    # if msg_length:
    #     print(f"Printing msg len: {msg_length}")
    #
    #     msg_length = int(msg_length)
    #
    #     msg = "Welcome to the server!"
    #     msg = f'{len(msg):<{HEADER_SIZE}}' + msg  # Nastavi fixny header size a za to doplni tu msg
    #     server_socket.sendto(bytes(msg.encode(FORMAT)), address)
    #     message, addr = server_socket.recvfrom(msg_length)
    #
    #     if message == DISCONNECT_MESSAGE:
    #         connected = False
    #
    #     print(f"[{addr}] {message}")
