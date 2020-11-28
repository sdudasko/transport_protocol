import socket
# import pickle
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
    udp_header_arr = b''.join([
        shared.get_fragment_order(order),
        shared.get_signal_message('DATA_SENDING'),
        shared.get_fragment_length(bytes_to_send),
        shared.get_number_of_fragments(),
        shared.get_crc(),
        shared.get_data(bytes_to_send)['data']
    ])

    client_socket.sendto(udp_header_arr, server_address)


def send(msg):
    _message = msg.encode(FORMAT).strip()
    msg_length = len(_message)
    send_length = str(msg_length).encode(FORMAT).strip()
    send_length += b' ' * (HEADER_SIZE - len(send_length))
    client_socket.sendto(send_length, server_address)
    client_socket.sendto(_message, server_address)


def send_init():
    udp_header_arr = b''.join([
        shared.get_fragment_order(0),
        shared.get_signal_message('CONNECTION_INITIALIZATION'),
        shared.get_fragment_length(b''),
        shared.get_number_of_fragments(),
        shared.get_crc()

    ])
    client_socket.sendto(udp_header_arr, server_address)


# 1. FIRST WE SEND INIT MESSAGE TO THE SERVER SO WE WANT TO INITIALIZE A CONNECTION
while True:
    send_init()  # We sent init message, now we listen for message from ACK from server
    message, server = client_socket.recvfrom(shared.get_max_size_of_receiving_packet())

    if message:
        # We got ack after init from server, now are "connected",
        # not really connected since UDP is connectionless but kind of

        if int.from_bytes(message[2:4], 'little') == 2:
            filename = "adad.png"
            size_of_file_to_send = os.path.getsize(filename)
            print(f"Size of file: {size_of_file_to_send}")

            i = 1
            with open(filename, 'rb') as file:
                bytes_to_send = file.read(config.header['MAX_ADDRESSING_SIZE_WITHOUT_HEADER'])

                send_piece_of_data(bytes_to_send, i)

                while bytes_to_send != b'':
                    i += 1
                    bytes_to_send = file.read(config.header['MAX_ADDRESSING_SIZE_WITHOUT_HEADER'])
                    send_piece_of_data(bytes_to_send, i)

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
