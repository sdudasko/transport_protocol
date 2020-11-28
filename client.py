import socket
import pickle
import config
import shared
import os
import sys

BLOCK_SIZE = 15
HEADER_SIZE = 14
DISCONNECT_MESSAGE = "!DISCONNECT"  # TODO - toto presunut:-)
FORMAT = 'utf-8'

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = (socket.gethostname(), 1234)
client_address = (socket.gethostname(), 1235)


def send_piece_of_data(bytes_to_send, order):
    udp_header_arr = (
        shared.get_fragment_order(order),
        shared.get_signal_message('DATA_SENDING'),
        shared.get_fragment_length(bytes_to_send),
        shared.get_number_of_fragments(),
        shared.get_crc(),
        shared.get_data(bytes_to_send)['data']
    )
    udp_header = pickle.dumps(udp_header_arr)
    data = b""
    # print(f"get_fragment_order: {sys.getsizeof(shared.get_fragment_order(order))}")
    # print(f"get_signal_message: {sys.getsizeof(shared.get_signal_message('DATA_SENDING'))}")
    # print(f"get_fragment_length: {sys.getsizeof(shared.get_fragment_length(bytes_to_send))}")
    # print(f"get_number_of_fragments: {sys.getsizeof(shared.get_number_of_fragments())}")
    # print(f"get_crc: {sys.getsizeof(shared.get_crc())}")
    # print(f"get_data: {len(shared.get_data(bytes_to_send)['data'])}")
    print("Here")
    print(udp_header)
    client_socket.sendto(udp_header + data, server_address)


def send(msg):
    message = msg.encode(FORMAT).strip()
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT).strip()
    send_length += b' ' * (HEADER_SIZE - len(send_length))
    client_socket.sendto(send_length, server_address)
    client_socket.sendto(message, server_address)


def send_init():
    udp_header_arr = (
        shared.get_fragment_order(0),
        shared.get_signal_message('CONNECTION_INITIALIZATION'),
        shared.get_fragment_length(b''),
        shared.get_number_of_fragments(),
        shared.get_crc(),
        shared.get_data(b'')['data']
    )
    udp_header = pickle.dumps(udp_header_arr)
    data = b""
    client_socket.sendto(udp_header + data, server_address)


# 1. FIRST WE SEND INIT MESSAGE TO THE SERVER SO WE WANT TO INITIALIZE A CONNECTION
while True:
    send_init()  # We sent init message, now we listen for message from ACK from server
    message, server = client_socket.recvfrom(shared.get_max_size_of_receiving_packet())

    if message:
        # We got ack after init from server, now are "connected",
        # not really connected since UDP is connectionless but kind of
        if pickle.loads(message)[1] == 2:
            filename = "alica.txt"
            os.path.getsize("alica.txt")
            with open("alica.txt", 'r') as file:
                bytes_to_send = file.read(config.header['MAX_ADDRESSING_SIZE_WITHOUT_HEADER'])
                print(f"Len: {len(bytes_to_send)}")
                # client_socket.sendto(bytes_to_send, server_address)
                send_piece_of_data(bytes_to_send, 1)

# send(DISCONNECT_MESSAGE)

# while True:
#
#     new_message = True
#     full_message = ''
#
#     while True:
#         # Receive response
#         message_len = 0
#
#         message, server = client_socket.recvfrom(16) # Value when to stop reading
#         print(message)
#         message = message.decode(FORMAT)
#         abc = bytes(message[:HEADER_SIZE], FORMAT)
#
#         if new_message:
#             if abc:
#                 message_len = int(abc)
#                 new_message = False
#                 print(message_len)
#
#         full_message += message
#
#         if len(full_message) - HEADER_SIZE == message_len:
#             print(f"Printing full message: {full_message}")
#             new_message = True
#             full_message = ''
#             print("in the branch")
