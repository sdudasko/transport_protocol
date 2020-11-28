import socket
import time
import struct
# import pickle
import shared

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
    message = msg.encode(FORMAT).strip()
    server_socket.sendto(message, address)


def send_ack(address):
    udp_header_arr = b''.join([
        shared.get_fragment_order(0),
        shared.get_signal_message('ACKNOWLEDGEMENT'),
        shared.get_fragment_order(0),
        shared.get_crc(),
        shared.get_data(b'')['data']
    ])
    server_socket.sendto(udp_header_arr, address)


# while True:
message, address = server_socket.recvfrom(MAX_DATA_SIZE)  # We are waiting for init message

if message:
    print(int.from_bytes(message[0:2], 'little'))
    print(int.from_bytes(message[2:4], 'little'))
    # If the message we got is initialization message
    if int.from_bytes(message[2:4], 'little') == config.signals['CONNECTION_INITIALIZATION']:

        send_ack(address)

        message, address = server_socket.recvfrom(MAX_DATA_SIZE)

        if message:
            print("HEADER...")
            print("ENDHEADER...")
            print(message[(config.header['HEADER_SIZE'] + 1):].decode('utf-8'))

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
