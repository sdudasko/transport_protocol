import socket
import pickle
import config
import shared
import os

BLOCK_SIZE = 15
HEADER_SIZE = 14
DISCONNECT_MESSAGE = "!DISCONNECT"  # TODO - toto presunut:-)
FORMAT = 'utf-8'

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = (socket.gethostname(), 1234)
client_address = (socket.gethostname(), 1235)

def send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER_SIZE - len(send_length))
    client_socket.sendto(send_length, server_address)
    client_socket.sendto(message, server_address)


def send_init():
    udp_header_arr = (
        shared.get_fragment_order(),
        shared.get_signal_message('CONNECTION_INITIALIZATION'),
        shared.get_fragment_order(),
        shared.get_crc(),
        shared.get_data()
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
            with open("alica.txt", 'rb') as file:
                bytes_to_send = file.read(config.header['MAX_ADDRESSING_SIZE_WITHOUT_HEADER'])
                client_socket.sendto(bytes_to_send, server_address)

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
