import socket
import pickle
import config

BLOCK_SIZE = 15
HEADER_SIZE = 14
DISCONNECT_MESSAGE = "!DISCONNECT" # TODO - toto presunut:-)
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


def get_fragment_order():
    return 0


def get_signal_message():
    return config.signals['CONNECTION_INITIALIZATION']


def get_fragment_length():
    return 0


def get_crc():
    return 0


def get_data():
    return b''


def send_init():
    udp_header_arr = (
        get_fragment_order(),
        get_signal_message(),
        get_fragment_order(),
        get_crc(),
        get_data()
    )
    udp_header = pickle.dumps(udp_header_arr)
    data = b""
    client_socket.sendto(udp_header + data, server_address)


# 1. FIRST WE SEND INIT MESSAGE TO THE SERVER SO WE WANT TO INITIALIZE A CONNECTION
send_init()

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
