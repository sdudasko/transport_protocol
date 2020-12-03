import math
import os
import socket

import config
import shared
import readline
import time
import threading


BLOCK_SIZE = 5
HEADER_SIZE = 14
FORMAT = 'utf-8'

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_address = (socket.gethostname(), 1235)

connection_acquired = False


def send_piece_of_data(bytes_to_send_arg, order, mismatch_simulation=False, nch=0):
    correct_data_crc = False
    if mismatch_simulation:
        correct_data_crc = shared.get_crc(bytes_to_send_arg)

    udp_header_arr = b''.join([
        shared.get_fragment_order(order),
        shared.get_signal_message('DATA_SENDING'),
        shared.get_fragment_length(bytes_to_send_arg),
        shared.get_number_of_fragments(nch),
        shared.get_crc(bytes_to_send_arg) if not mismatch_simulation else correct_data_crc,
        shared.get_data(bytes_to_send_arg, mismatch_simulation)['data']
    ])

    client_socket.sendto(udp_header_arr, server_address)


def send_filename_message(filename_arg, sign='FILENAME'):  # _arg because of shadowing the outer scope var name

    udp_header_arr = b''.join([
        shared.get_fragment_order(1),  # Message with filename has order number 1, but it does not matter really
        shared.get_signal_message(sign),
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


def send_init(sign = 'CONNECTION_INITIALIZATION'):
    udp_header_arr = b''.join([
        shared.get_fragment_order(0),
        shared.get_signal_message(sign),
        shared.get_fragment_length(b''),
        shared.get_number_of_fragments(),
        shared.get_crc(b'')

    ])
    client_socket.sendto(udp_header_arr, server_address)

def send_keep_alive_ack():
    udp_header_arr = b''.join([
        shared.get_fragment_order(0),
        shared.get_signal_message('KEEP_ALIVE_ACK'),
        shared.get_fragment_length(b''),
        shared.get_number_of_fragments(),
        shared.get_crc(b'')

    ])
    client_socket.sendto(udp_header_arr, server_address)


def listen_for_keep_alive():
    while True:
        ms, srv = client_socket.recvfrom(shared.get_max_size_of_receiving_packet())
        if shared.transl(ms, 2, 4) == config.signals['KEEP_ALIVE']:
            print("Prislo ACK-cko zo servera")
            send_keep_alive_ack()
        time.sleep(6)


def handle_client_request_to_send_data(message, server, filename='', already_connected=False, message_for_stdin=''):

    if message:
        # We got ack after init from server, now are "connected",
        # not really connected since UDP is connectionless but kind of.
        if (shared.transl(message, 2, 4) == 2) or already_connected:

            # 2. SENDING FILENAME
            if filename == '':
                new_file = open("_tmp_stdin.txt", 'wb')
                new_file.write(message_for_stdin.encode(config.common['FORMAT']))
                new_file.close()
                send_filename_message('_tmp_stdin.txt', 'STDIN')
                filename = '_tmp_stdin.txt'
            else:
                send_filename_message(filename)

            max_addressing_size_without_header = shared.get_max_addressing_size_without_header()

            with open(filename, 'rb') as file:

                bytes_to_send = file.read(max_addressing_size_without_header)
                total_fragments = math.ceil(
                    os.stat(filename).st_size / max_addressing_size_without_header)
                client_block_of_fragments = {}

                i = 1
                n = 0
                z = False
                k = False
                total_mismatchs = 0
                while bytes_to_send != b'':

                    # Refactor that, not needed anymore in this state
                    # ------------------
                    if i == 1 and not z: # Ak chces zasielat v 1. packete simulaciu tak treba tak sem True
                        send_piece_of_data(bytes_to_send, i, False, nch=total_fragments)
                        client_block_of_fragments[i] = bytes_to_send
                        i += 1
                        z = True
                    # ------------------

                    if total_fragments < BLOCK_SIZE:
                        print(f"Was last")

                        if (i - 1) == total_fragments:
                            print(f"Be: {(i - 1)} {total_fragments}")
                            message, server = client_socket.recvfrom(shared.get_max_size_of_receiving_packet())

                            if shared.transl(message, 2, 4) == config.signals['FRAGMENT_ACK_CRC_MISMATCH']:
                                order_of_first_crc_mismatched_fragment = int.from_bytes(message[0:2], 'little')

                                tmp_client_block_of_fragments = client_block_of_fragments
                                client_block_of_fragments = {}  # TODO - does this work? Check if it does not del the ref

                                send_piece_of_data(
                                    tmp_client_block_of_fragments[order_of_first_crc_mismatched_fragment],
                                    order_of_first_crc_mismatched_fragment, nch=total_fragments)

                                client_block_of_fragments[i + n * BLOCK_SIZE] = tmp_client_block_of_fragments[
                                    order_of_first_crc_mismatched_fragment]
                                i += 1

                                del tmp_client_block_of_fragments[order_of_first_crc_mismatched_fragment]


                    bytes_to_send = file.read(max_addressing_size_without_header)


                    # Simulation of CRC mismatch on 3. fragment
                    if k == False and i == 3:
                        send_piece_of_data(bytes_to_send, i + n * BLOCK_SIZE, nch=total_fragments,
                                           mismatch_simulation=True)
                        k = True
                    else:
                        send_piece_of_data(bytes_to_send, i + n * BLOCK_SIZE, nch=total_fragments,
                                           mismatch_simulation=False)

                    # Storing these data here just for backup, then we will overwrite those, we could probably
                    # solve it even without this helper variable with some seek func.
                    client_block_of_fragments[i + n * BLOCK_SIZE] = bytes_to_send
                    i += 1

                    # We sent BLOCK_SIZE number of fragments, now we wait for reply from server.
                    # If we got everything right we get ack with permission to send next block of data.
                    # If there was an error, we get n msgs where every msg tells in ORDER which fragment was corrupted.

                    if (i + total_mismatchs - 1) == BLOCK_SIZE:
                        total_mismatchs = 0

                        message, server = client_socket.recvfrom(shared.get_max_size_of_receiving_packet())

                        if shared.transl(message, 2, 4) == config.signals['FRAGMENT_ACK_OK']:
                            # Next block has already resolved crc mismatches, if they carry on sending mistakes,
                            # they will be stored in this array in next cycle so it's not a problem.
                            client_block_of_fragments = {}
                        elif shared.transl(message, 2, 4) == config.signals['FRAGMENT_ACK_CRC_MISMATCH']:

                            order_of_first_crc_mismatched_fragment = shared.transl(message, 0, 2)

                            tmp_client_block_of_fragments = client_block_of_fragments
                            client_block_of_fragments = {}

                            send_piece_of_data(tmp_client_block_of_fragments[order_of_first_crc_mismatched_fragment],
                                               order_of_first_crc_mismatched_fragment, nch=total_fragments)

                            client_block_of_fragments[i + n * BLOCK_SIZE] = tmp_client_block_of_fragments[
                                order_of_first_crc_mismatched_fragment]

                            # i += 1
                            total_mismatchs += 1

                            del tmp_client_block_of_fragments[order_of_first_crc_mismatched_fragment]

                            # TODO - more errors in single block
                            # -1 bcs we have already received one so this will run only if more than one crc mismatch.
                            for fragment_with_crc_mismatch in range(shared.transl(message, 8, 10)):  # TODO
                                pass

                        elif shared.transl(message, 2, 4) == config.signals['KEEP_ALIVE']:
                            pass
                            # while shared.transl(message, 2, 4) == config.signals['FRAGMENT_ACK_OK']:
                            #     print("Semka :)")
                            #     print(message)


                        i = 1
                        n += 1

            # File is all read

        # listen_for_keep_alive()


def client_prompt_ip(prompt, prefill='127.0.0.1'):
    readline.set_startup_hook(lambda: readline.insert_text(prefill))
    try:
        return input(prompt)
    finally:
        readline.set_startup_hook()

def client_prompt_port(prompt, prefill='1234'):
    readline.set_startup_hook(lambda: readline.insert_text(prefill))
    try:
        return input(prompt)
    finally:
        readline.set_startup_hook()


started_waiting_for_ack = False
while True:
    # 1. FIRST WE SEND INIT MESSAGE TO THE SERVER SO WE WANT TO INITIALIZE A CONNECTION

    if not connection_acquired:
        print("Zadaj cielovu IP adresu: ")
        server_ip_address = client_prompt_ip("")
        print("Zadaj adresu cieloveho portu: ")
        server_port = client_prompt_port("")

        server_address = (server_ip_address, int(server_port))

        send_init()  # We sent init message, now we listen for message from ACK from server
        message, server = client_socket.recvfrom(shared.get_max_size_of_receiving_packet())
        print(message)
        connection_acquired = True

    sending_file_msg = 'Chces posielat subor?'
    sending_file = input("%s (y/N) " % sending_file_msg).lower() == 'y'

    if sending_file:
        print("Zadaj cestu ku suboru:")
        filename = input("")
        handle_client_request_to_send_data(message, server, filename=filename)
    else:
        print("Zadaj spravu: ")
        _stdin = input("")
        handle_client_request_to_send_data(message, server, message_for_stdin=_stdin)

    if not started_waiting_for_ack:
        started_waiting_for_ack = True
        print("tru")
        t1 = threading.Thread(target=listen_for_keep_alive)
        t1.start()

    msg = 'Chces ukoncit spojenie?'
    end_connection = input("%s (y/N) " % msg).lower() == 'y'

    if not end_connection:
        pass
    else:
        print("Ending connection")
        send_init('CONNECTION_CLOSE_REQUEST') #taka recyklacia, asi premenovat func

        while True:
            message, server = client_socket.recvfrom(shared.get_max_size_of_receiving_packet())
            if shared.transl(message, 2, 4) == config.signals['CONNECTION_CLOSE_ACK']:
                connection_acquired = False
                break


