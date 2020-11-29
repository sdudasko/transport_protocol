import socket

# import pickle
import config
import shared

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

            i = 1
            n = 0
            with open(filename, 'rb') as file:

                bytes_to_send = file.read(config.header['MAX_ADDRESSING_SIZE_WITHOUT_HEADER'])

                while bytes_to_send != b'':
                    # Uncomment if you want to send trailing data in 1st fragment.
                    # if i == 1 + 1:
                    #     send_piece_of_data(bytes_to_send, i, True)
                    # else:
                    #     send_piece_of_data(bytes_to_send, i)

                    bytes_to_send = file.read(config.header['MAX_ADDRESSING_SIZE_WITHOUT_HEADER'])
                    send_piece_of_data(bytes_to_send, i + n * BLOCK_SIZE)

                    # We sent BLOCK_SIZE number of fragments, now we wait for reply from server.
                    # If we got everything right we get ack with permission to send next block of data.
                    # If there was an error, we get n msgs where every msg tells in ORDER which fragment was corrupted.
                    if i == BLOCK_SIZE:
                        message, server = client_socket.recvfrom(shared.get_max_size_of_receiving_packet())

                        if int.from_bytes(message[2:4], 'little') == config.signals['FRAGMENT_ACK_OK']:
                            pass # Everything is fine, we can send more data
                        elif int.from_bytes(message[2:4], 'little') == config.signals['FRAGMENT_ACK_CRC_MISMATCH']:
                            pass
                        else:
                            raise ValueError("We got nor OK ACK or CRC MISMATCH.")

                        i = 1
                        n += 1

                    i += 1
