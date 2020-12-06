import os
import socket
import threading
import time

import config
import shared

BLOCK_SIZE = 5
HEADER_SIZE = 14
MAX_DATA_SIZE = 1500
kill_threads = False

FORMAT = 'utf-8'

received_packets_count = 0
total_crc_mismatched = 0
connection_acquired = False
started_waiting_for_ack = False

address = ""
server_socket = ""

failed_to_ack_keep_alive = False
last_ack = time.time()

def send_keepalive():
    global last_ack
    global address
    global failed_to_ack_keep_alive
    global connection_acquired
    global kill_threads

    if kill_threads:
        threading.Timer(10.0, send_keepalive).cancel()
    else:
        threading.Timer(10.0, send_keepalive).start()
        kill_threads = False
    if not kill_threads:
        udp_header_arr = b''.join([
            shared.get_fragment_order(0),
            shared.get_signal_message('KEEP_ALIVE'),
            shared.get_fragment_length(b''),
            shared.get_number_of_fragments(),
            shared.get_crc(b''),
            shared.get_data(b'')['data']
        ])

        if (time.time() - last_ack) > config.common['DISCONNECT_AFTER_N_SECONDS']:
            print("Client failed to ACK keep alive")
            connection_acquired = False
            failed_to_ack_keep_alive = True
            last_ack = time.time()
            send_ack(address, 'CONNECTION_CLOSE_ACK')

        else:
            if not server_socket._closed:
                server_socket.sendto(udp_header_arr, address)

        if not server_socket._closed:
            message, address = server_socket.recvfrom(MAX_DATA_SIZE)

            if message and shared.transl(message, 2, 4) == config.signals['KEEP_ALIVE_ACK']:
                last_ack = time.time()
        return


def send_ack(address, sign='ACKNOWLEDGEMENT', fragment_order=0, number_of_fragments=0):
    udp_header_arr = b''.join([
        shared.get_fragment_order(fragment_order),
        shared.get_signal_message(sign),
        shared.get_fragment_length(b''),
        shared.get_number_of_fragments(number_of_fragments),
        shared.get_crc(b''),
        shared.get_data(b'')['data']
    ])
    server_socket.sendto(udp_header_arr, address)


def check_for_crc_match(compared_crc, data):
    calculated_crc = shared.calculate_crc(data)
    calculated_crc = int(calculated_crc[2:], 16)

    return int.from_bytes(compared_crc, 'little') == calculated_crc


def handle_server_responses():
    global address
    global kill_threads
    message, address = server_socket.recvfrom(MAX_DATA_SIZE)  # 1. WAITING FOR INIT MESSAGE

    if shared.transl(message, 2, 4) == config.signals['KEEP_ALIVE_ACK']:
        return

    input_was_stdin = False
    global connection_acquired
    filename_to_print = ""

    if shared.transl(message, 2, 4) == config.signals['CONNECTION_CLOSE_REQUEST']:
        send_ack(address, 'CONNECTION_CLOSE_ACK')
        connection_acquired = False

    if message:
        i = 0
        c = 0
        received_packets_count = 0
        total_crc_mismatched = 0

        if (shared.transl(message, 2, 4) == config.signals['CONNECTION_INITIALIZATION']) or connection_acquired:

            if not connection_acquired:
                # 1. SENDING ACK TO INIT COMMUNICATION AND AT THIS POINT INITIALIZATION IS DONE
                send_ack(address)

                # 2. RECEIVING NAME OF FILE AND CREATING BLANK FILE WITH CORRECT NAME
                message, address = server_socket.recvfrom(MAX_DATA_SIZE)
                connection_acquired = True

            if (message and shared.transl(message, 2, 4) == config.signals['KEEP_ALIVE_ACK']) or (message and shared.transl(message, 2, 4) == config.signals['FILENAME']) or (message and shared.transl(message, 2, 4) == config.signals['STDIN']):
                if shared.transl(message, 2, 4) == config.signals['STDIN']:
                    input_was_stdin = True

                hl = config.header['HEADER_SIZE'] + int.from_bytes(message[4:8], 'little')
                new_file = open("received_files/"+message[(config.header['HEADER_SIZE']):hl].decode('utf-8'), 'wb')
                filename_to_print = message[(config.header['HEADER_SIZE']):hl].decode('utf-8')

                # 3. RECEIVING FIRST FRAGMENT OF 1st block
                message, address = server_socket.recvfrom(MAX_DATA_SIZE)
                if message and shared.transl(message, 2, 4) == config.signals['KEEP_ALIVE_ACK']:
                    message, address = server_socket.recvfrom(MAX_DATA_SIZE)

                server_block_of_fragments = {}
                mismatched_fragment_order_numbers = list()

                if message and (shared.transl(message, 2, 4) == config.signals['DATA_SENDING']) or (shared.transl(message, 2, 4) == config.signals['KEEP_ALIVE_ACK']):
                    received_packets_count += 1
                    i = 1  #

                    dontbreakonfirstiteration = False
                    if not check_for_crc_match(message[10:14], message[14:]):
                        mismatched_fragment_order_numbers.append(shared.transl(message, 0, 2))
                        print(f"CRC MISMATCH: Prijaty fragment s poradovym cislom: {shared.transl(message, 0, 2)}")

                        if int.from_bytes(message[8:10], 'little') < BLOCK_SIZE:
                            dontbreakonfirstiteration = True

                    server_block_of_fragments[shared.transl(message, 0, 2)] = message[(config.header['HEADER_SIZE']):]

                    while True:

                        if (received_packets_count - total_crc_mismatched) == int.from_bytes(message[8:10], 'little'): # Prijali sme posledny blok
                            c = 0

                            while len(mismatched_fragment_order_numbers) > 0:
                                total_crc_mismatched += 1

                                send_ack(address, 'FRAGMENT_ACK_CRC_MISMATCH', mismatched_fragment_order_numbers[c],
                                         len(mismatched_fragment_order_numbers))
                                del mismatched_fragment_order_numbers[c]
                                c += 1

                            if not dontbreakonfirstiteration:
                                for key, value in server_block_of_fragments.items():
                                    new_file.write(value)
                                # send_ack(address, 'FRAGMENT_ACK_OK')

                            # if os.path.exists("received_files/_tmp_stdin.txt"):
                            #     file_to_read = open("received_files/_tmp_stdin.txt", "r")
                            #     data = file_to_read.read()
                            #     print("Prichadzajuca sprava: " + data)

                            if not dontbreakonfirstiteration:
                                return
                            else:
                                dontbreakonfirstiteration = False

                        message, address = server_socket.recvfrom(MAX_DATA_SIZE)
                        if message and shared.transl(message, 2, 4) == config.signals['KEEP_ALIVE_ACK']:
                            message, address = server_socket.recvfrom(MAX_DATA_SIZE)
                        if check_for_crc_match(message[10:14], message[14:]):
                            print(f"OK: Prijaty fragment s poradovym cislom: {shared.transl(message, 0, 2)}")

                        received_packets_count += 1

                        order_n = shared.transl(message, 0, 2)

                        server_block_of_fragments[order_n] = message[(config.header['HEADER_SIZE']):]

                        if not check_for_crc_match(message[10:14], message[14:]):
                            mismatched_fragment_order_numbers.append(shared.transl(message, 0, 2))
                            print(f"CRC MISMATCH: Prijaty fragment s poradovym cislom: {shared.transl(message, 0, 2)}")

                        i += 1

                        if i == BLOCK_SIZE: # Sme na k-tom fragmente, k je pocet blokov

                            if len(mismatched_fragment_order_numbers) == 0:

                                send_ack(address, 'FRAGMENT_ACK_OK')

                                for key, value in server_block_of_fragments.items():
                                    new_file.write(value)
                                server_block_of_fragments.clear()  # Some garbage collection

                            else:  # We have some data that did not pass CRC test so send information about that
                                c = 0

                                while len(mismatched_fragment_order_numbers) > 0:
                                    total_crc_mismatched += 1
                                    send_ack(address, 'FRAGMENT_ACK_CRC_MISMATCH', mismatched_fragment_order_numbers[c],
                                             len(mismatched_fragment_order_numbers))
                                    del mismatched_fragment_order_numbers[c]
                                    c += 1
                            i = 0
                        if (received_packets_count - total_crc_mismatched) == int.from_bytes(message[8:10], 'little'):
                            if input_was_stdin:
                                pass
                                # file_to_read = open("received_files/_tmp_stdin.txt", "r")
                                # data = file_to_read.read()
                                # print("Prichadzajuca sprava: " + data)
                            else:
                                print("Subor bol prijaty a ulozeny na ceste:" + os.path.abspath(
                                    "received_files/" + filename_to_print))
                    if (received_packets_count - total_crc_mismatched) == int.from_bytes(message[8:10], 'little'):
                        return
                else:
                    raise ValueError("We were expecting to get filename.")


    else:
        pass


def setup_server(port_number):
    global server_socket
    global server_address

    SERVER = "127.0.0.1"
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = (SERVER, port_number)

    server_socket.bind(server_address)
    print(f"[LISTENING] Server is listening on {SERVER}:{port_number}")

refresh_socket = False

def server_close():
    global server_socket
    global server_address
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    server_socket.close()

server_set = False
def server_behaviour(port_number = 1236):
    global started_waiting_for_ack
    global server_socket
    global switch_sides_toggle
    global server_set
    global kill_threads

    if not server_set:
        server_set = True
        setup_server(port_number)

    while True:

        try:
            if os.path.exists("received_files/_tmp_stdin.txt"):
                os.remove("received_files/_tmp_stdin.txt")

            handle_server_responses()
            kill_threads = False

            if os.path.exists("received_files/_tmp_stdin.txt"):
                file_to_read = open("received_files/_tmp_stdin.txt", "r")
                data = file_to_read.read()
                print("Prichadzajuca sprava: " + data)

            if not started_waiting_for_ack:
                started_waiting_for_ack = True
                t1 = threading.Thread(target=send_keepalive)
                t1.start()
                t1.join()
        except:
            return