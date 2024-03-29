import socket
import shared
import config
import sys
import os

BLOCK_SIZE = 5
HEADER_SIZE = 14
MAX_DATA_SIZE = 1500

SERVER = socket.gethostbyname(socket.gethostname())
FORMAT = 'utf-8'
nf_prefix = "bbb"

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = (socket.gethostname(), 1234)

server_socket.bind(server_address)
print(f"[LISTENING] Server is listening on {SERVER}")

received_packets_count = 0
total_crc_mismatched = 0

def send(msg, address):
    message = msg.encode(FORMAT).strip()
    server_socket.sendto(message, address)


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

input_was_stdin = False

message, address = server_socket.recvfrom(MAX_DATA_SIZE)  # 1. WAITING FOR INIT MESSAGE

if message:

    # If the message we got is initialization message
    if shared.transl(message, 2, 4) == config.signals['CONNECTION_INITIALIZATION']:

        # 1. SENDING ACK TO INIT COMMUNICATION AND AT THIS POINT INITIALIZATION IS DONE
        send_ack(address)

        # 2. RECEIVING NAME OF FILE AND CREATING BLANK FILE WITH CORRECT NAME
        message, address = server_socket.recvfrom(MAX_DATA_SIZE)

        if (message and shared.transl(message, 2, 4) == config.signals['FILENAME']) or (message and shared.transl(message, 2, 4) == config.signals['STDIN']):
            if shared.transl(message, 2, 4) == config.signals['STDIN']:
                input_was_stdin = True

            hl = config.header['HEADER_SIZE'] + int.from_bytes(message[4:8], 'little')
            new_file = open(nf_prefix + message[(config.header['HEADER_SIZE']):hl].decode('utf-8'), 'wb')

            # 3. RECEIVING FIRST FRAGMENT OF 1st block
            message, address = server_socket.recvfrom(MAX_DATA_SIZE)

            server_block_of_fragments = {}
            mismatched_fragment_order_numbers = list()

            if message and shared.transl(message, 2, 4) == config.signals['DATA_SENDING']:
                received_packets_count += 1
                i = 1  #
                order_n = shared.transl(message, 0, 2)

                if not check_for_crc_match(message[10:14], message[14:]):
                    mismatched_fragment_order_numbers.append(shared.transl(message, 0, 2))
                    print(f"################## CRC MISMATCH vo fragmente {order_n} ! ##################")

                server_block_of_fragments[order_n] = message[(config.header['HEADER_SIZE']):]

                while True:

                    if (received_packets_count - total_crc_mismatched) == int.from_bytes(message[8:10], 'little'):
                        c = 0

                        while len(mismatched_fragment_order_numbers) > 0:
                            total_crc_mismatched += 1

                            send_ack(address, 'FRAGMENT_ACK_CRC_MISMATCH', mismatched_fragment_order_numbers[c],
                                     len(mismatched_fragment_order_numbers))
                            del mismatched_fragment_order_numbers[c]
                            c += 1

                        for key, value in server_block_of_fragments.items():
                            new_file.write(value)
                        print(f"Zapisovaine posledneho bloku.")

                        if input_was_stdin:
                            file_to_read = open("_tmp_stdin.txt", "r")
                            data = file_to_read.read()
                            print(data)
                            os.remove(nf_prefix + "_tmp_stdin.txt")

                        break

                    message, address = server_socket.recvfrom(MAX_DATA_SIZE)
                    received_packets_count += 1
                    order_n = shared.transl(message, 0, 2)

                    server_block_of_fragments[order_n] = message[(config.header['HEADER_SIZE']):]

                    if not check_for_crc_match(message[10:14], message[14:]):  # TODO - send wrong ack
                        mismatched_fragment_order_numbers.append(shared.transl(message, 0, 2))
                        print(f"################## CRC MISMATCH vo fragmente {order_n} ! ##################")

                    i += 1

                    if i == BLOCK_SIZE:
                        if len(mismatched_fragment_order_numbers) == 0:

                            send_ack(address, 'FRAGMENT_ACK_OK')

                            for key, value in server_block_of_fragments.items():
                                new_file.write(value)
                            server_block_of_fragments.clear() # Some garbage collection
                        else:  # We have some data that did not pass CRC test so send information about that
                            c = 0

                            while len(mismatched_fragment_order_numbers) > 0:
                                total_crc_mismatched += 1
                                send_ack(address, 'FRAGMENT_ACK_CRC_MISMATCH', mismatched_fragment_order_numbers[c],
                                         len(mismatched_fragment_order_numbers))
                                del mismatched_fragment_order_numbers[c]
                                c += 1
                        i = 0

            else:
                raise ValueError("We were expecting to get filename.")
    else:
        raise ValueError("We were expecting to get init message.")



else:
    pass
