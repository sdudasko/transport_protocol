import socket
import shared
import config
import sys

BLOCK_SIZE = 5
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


def send_ack(address, sign='ACKNOWLEDGEMENT', fragment_order=0, number_of_fragments = 0):
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


message, address = server_socket.recvfrom(MAX_DATA_SIZE)  # 1. WAITING FOR INIT MESSAGE

if message:

    # If the message we got is initialization message
    if int.from_bytes(message[2:4], 'little') == config.signals['CONNECTION_INITIALIZATION']:

        # 1. SENDING ACK TO INIT COMMUNICATION AND AT THIS POINT INITIALIZATION IS DONE
        send_ack(address)

        # 2. RECEIVING NAME OF FILE AND CREATING BLANK FILE WITH CORRECT NAME
        message, address = server_socket.recvfrom(MAX_DATA_SIZE)

        if message and int.from_bytes(message[2:4], 'little') == config.signals['FILENAME']:

            hl = config.header['HEADER_SIZE'] + int.from_bytes(message[4:8], 'little')
            new_file = open("bbb" + message[(config.header['HEADER_SIZE']):hl].decode('utf-8'), 'wb')

            # 3. RECEIVING FIRST FRAGMENT OF 1st block
            message, address = server_socket.recvfrom(MAX_DATA_SIZE)
            server_block_of_fragments = []
            mismatched_fragment_order_numbers = list()

            if message and int.from_bytes(message[2:4], 'little') == config.signals['DATA_SENDING']:
                i = 1  #

                if not check_for_crc_match(message[10:14], message[14:]):
                    mismatched_fragment_order_numbers.append(int.from_bytes(message[0:2], 'little'))
                    print("########################### CRC MISMATCH! ###########################")

                # Musime uz tu dat zapis prveho lebo sme ho dostali pri sprave s tym, ze zasielame data
                # new_file.write(message[(config.header['HEADER_SIZE']):])
                server_block_of_fragments.append(message[(config.header['HEADER_SIZE']):])
                while True:
                    message, address = server_socket.recvfrom(MAX_DATA_SIZE)
                    # new_file.write(message[(config.header['HEADER_SIZE']):])
                    server_block_of_fragments.append(message[(config.header['HEADER_SIZE']):])

                    if not check_for_crc_match(message[10:14], message[14:]):  # TODO - send wrong ack
                        mismatched_fragment_order_numbers.append(int.from_bytes(message[0:2], 'little'))
                        # print("########################### CRC MISMATCH! ###########################")

                    i += 1

                    if i == BLOCK_SIZE:
                        new_file.write(message[(config.header['HEADER_SIZE']):] * BLOCK_SIZE)

                        if len(mismatched_fragment_order_numbers) == 0:
                            print("Sending OK")
                            send_ack(address, 'FRAGMENT_ACK_OK')
                            i = 0
                        else:  # We have some data that did not pass CRC test so send information about that
                            c = 0

                            while len(mismatched_fragment_order_numbers) > 0:
                                send_ack(address, 'FRAGMENT_ACK_CRC_MISMATCH', mismatched_fragment_order_numbers[c], len(mismatched_fragment_order_numbers))
                                del mismatched_fragment_order_numbers[c]
                                c += 1

                    if int.from_bytes(message[4:8], 'little') != config.header[
                        'MAX_ADDRESSING_SIZE_WITHOUT_HEADER']:  # TODO - toto porovnat lepsie
                        message, address = server_socket.recvfrom(MAX_DATA_SIZE)
                        # new_file.write(message[(config.header['HEADER_SIZE']):])
                        server_block_of_fragments.append(message[(config.header['HEADER_SIZE']):])
                        break
            else:
                raise ValueError("We were expecting to get filename.")
    else:
        raise ValueError("We were expecting to get init message.")



else:
    pass
