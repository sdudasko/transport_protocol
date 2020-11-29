import socket
import time
import struct
# import pickle
import shared

import config

BLOCK_SIZE = 15
HEADER_SIZE = 14
MAX_DATA_SIZE = 1500

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
        shared.get_crc(b''),
        shared.get_data(b'')['data']
    ])
    server_socket.sendto(udp_header_arr, address)


def check_for_crc_match(compared_crc, data):

    calculated_crc = shared.calculate_crc(data)
    calculated_crc = int(calculated_crc[2:], 16)

    return int.from_bytes(compared_crc, 'little') == calculated_crc


message, address = server_socket.recvfrom(MAX_DATA_SIZE)  # 1. WAITING FOR INIT MESSAGE

if message:

    # If the message we got is initialization message
    if int.from_bytes(message[2:4], 'little') == config.signals['CONNECTION_INITIALIZATION']:

        # 1. SENDING ACK TO INIT COMMUNICATION AND AT THIS POINT INITIALIZATION IS DONE
        send_ack(address)

        # 2. RECEIVING NAME OF FILE AND CREATING BLANK FILE WITH CORRECT NAME
        message, address = server_socket.recvfrom(MAX_DATA_SIZE)

        if message and int.from_bytes(message[2:4], 'little') == config.signals['FILENAME']:

            new_file = open("novy_subor_" +
                            message[
                            (config.header['HEADER_SIZE']):
                            (config.header['HEADER_SIZE'] + int.from_bytes(message[4:8], 'little'))
                            ].decode('utf-8'), 'wb'
                            )

            message, address = server_socket.recvfrom(MAX_DATA_SIZE)

            if message and int.from_bytes(message[2:4], 'little') == config.signals['DATA_SENDING']:

                if not check_for_crc_match(message[10:14], message[14:]):
                    print("###########################")
                    print("CRC MISMATCH!")
                    print("###########################")

                # message, address = server_socket.recvfrom(MAX_DATA_SIZE)
                new_file.write(message[(config.header[
                    'HEADER_SIZE']):])  # Musime uz tu dat zapis prveho lebo sme ho dostali pri sprave s tym, ze zasielame data

                while True:
                    message, address = server_socket.recvfrom(MAX_DATA_SIZE)
                    new_file.write(message[(config.header['HEADER_SIZE']):])

                    if not check_for_crc_match(message[10:14], message[14:]):
                        print("###########################")
                        print("CRC MISMATCH!")
                        print("###########################")

                    if int.from_bytes(message[4:8], 'little') != config.header['MAX_ADDRESSING_SIZE_WITHOUT_HEADER']:
                        message, address = server_socket.recvfrom(MAX_DATA_SIZE)
                        new_file.write(message[(config.header['HEADER_SIZE']):])
                        break
            else:
                raise ValueError("We were expecting to get filename.")
    else:
        raise ValueError("We were expecting to get init message.")



else:
    pass
