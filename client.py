import socket

import config
import shared
import sys

BLOCK_SIZE = 5
HEADER_SIZE = 14
DISCONNECT_MESSAGE = "!DISCONNECT"  # TODO - toto presunut:-)
FORMAT = 'utf-8'

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = (socket.gethostname(), 1234)
client_address = (socket.gethostname(), 1235)


def send_piece_of_data(bytes_to_send_arg, order, mismatch_simulation=False):
    correct_data_crc = False
    if mismatch_simulation:
        correct_data_crc = shared.get_crc(bytes_to_send_arg)

    udp_header_arr = b''.join([
        shared.get_fragment_order(order),
        shared.get_signal_message('DATA_SENDING'),
        shared.get_fragment_length(bytes_to_send_arg),
        shared.get_number_of_fragments(),
        shared.get_crc(bytes_to_send_arg) if not mismatch_simulation else correct_data_crc,
        shared.get_data(bytes_to_send_arg, mismatch_simulation)['data']
    ])

    client_socket.sendto(udp_header_arr, server_address)


def send_filename_message(filename_arg):  # _arg because of shadowing the outer scope var name

    udp_header_arr = b''.join([
        shared.get_fragment_order(1),  # Message with filename has order number 1, but it does not matter really
        shared.get_signal_message('FILENAME'),
        shared.get_fragment_length(filename_arg),
        shared.get_number_of_fragments(),
        shared.get_crc(b''),  # TODO - Chceme tu robit CRC ?
        shared.get_data(filename_arg)['data']
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
        shared.get_crc(b'')

    ])
    client_socket.sendto(udp_header_arr, server_address)


while True:

    # 1. FIRST WE SEND INIT MESSAGE TO THE SERVER SO WE WANT TO INITIALIZE A CONNECTION
    send_init()  # We sent init message, now we listen for message from ACK from server
    message, server = client_socket.recvfrom(shared.get_max_size_of_receiving_packet())

    if message:
        # We got ack after init from server, now are "connected",
        # not really connected since UDP is connectionless but kind of.
        if int.from_bytes(message[2:4], 'little') == 2:

            # 2. SENDING FILENAME
            filename = "adad.png"
            send_filename_message(filename)

            with open(filename, 'rb') as file:

                bytes_to_send = file.read(config.header['MAX_ADDRESSING_SIZE_WITHOUT_HEADER'])

                client_block_of_fragments = {}

                i = 1
                n = 0
                z = False
                while bytes_to_send != b'':
                    # Uncomment if you want to send trailing data in 1st fragment. TOD0 - by some option then
                    # ------------------
                    if i == 1 and not z:
                        send_piece_of_data(bytes_to_send, i, True)
                        client_block_of_fragments[i] = bytes_to_send
                        # client_block_of_fragments.append(bytes_to_send)
                        i += 1
                        z = True
                    # ------------------

                    bytes_to_send = file.read(config.header['MAX_ADDRESSING_SIZE_WITHOUT_HEADER'])

                    send_piece_of_data(bytes_to_send, i + n * BLOCK_SIZE)
                    # Storing these data here just for backup, then we will overwrite those, we could probably
                    # solve it even without this helper variable with some seek func.
                    # client_block_of_fragments.append(bytes_to_send)
                    client_block_of_fragments[i + n * BLOCK_SIZE] = bytes_to_send
                    i += 1

                    # We sent BLOCK_SIZE number of fragments, now we wait for reply from server.
                    # If we got everything right we get ack with permission to send next block of data.
                    # If there was an error, we get n msgs where every msg tells in ORDER which fragment was corrupted.
                    if (i - 1) == BLOCK_SIZE:

                        message, server = client_socket.recvfrom(shared.get_max_size_of_receiving_packet())

                        if int.from_bytes(message[2:4], 'little') == config.signals['FRAGMENT_ACK_OK']:
                            # Next block has already resolved crc mismatches, if they carry on sending mistakes,
                            # they will be stored in this array in next cycle so it's not a problem.
                            client_block_of_fragments = []
                        elif int.from_bytes(message[2:4], 'little') == config.signals['FRAGMENT_ACK_CRC_MISMATCH']:
                            tmp_client_block_of_fragments = client_block_of_fragments
                            client_block_of_fragments = []  # TODO - does this work? Check if it does not del the ref

                            order_of_first_crc_mismatched_fragment = list(tmp_client_block_of_fragments.keys())[0]
                            send_piece_of_data(tmp_client_block_of_fragments[order_of_first_crc_mismatched_fragment], i + n * BLOCK_SIZE)
                            print(tmp_client_block_of_fragments[order_of_first_crc_mismatched_fragment])
                            # client_block_of_fragments.append(tmp_client_block_of_fragments[0])
                            client_block_of_fragments[i + n * BLOCK_SIZE] = next(iter(tmp_client_block_of_fragments))
                            i += 1

                            del tmp_client_block_of_fragments[0]

                            # -1 bcs we have already received one so this will run only if more than one crc mismatch.
                            for fragment_with_crc_mismatch in range(int.from_bytes(message[8:10], 'little') - 1):
                                message, server = client_socket.recvfrom(shared.get_max_size_of_receiving_packet())

                                print("d")
                                send_piece_of_data(tmp_client_block_of_fragments[0], i + n * BLOCK_SIZE)
                                del tmp_client_block_of_fragments[0]
                                client_block_of_fragments.append(bytes_to_send)
                                i += 1
                        else:
                            raise ValueError("We got nor OK ACK or CRC MISMATCH.")

                        i = 0
                        n += 1
