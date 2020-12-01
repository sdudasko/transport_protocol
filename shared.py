import config
import crcmod


def get_max_size_of_receiving_packet():  # TODO - toto si musi vediet uzivatel navolit, zatial dajme max, co moze byt
    return 1500


def get_max_size_of_receiving_packet_without_header():  # TODO - toto si musi vediet uzivatel navolit, zatial dajme max, co moze byt
    return 1456


def get_fragment_order(order):
    order = order.to_bytes(2, byteorder='little')
    return order


def get_signal_message(signal):
    sign = config.signals[signal].to_bytes(2, byteorder='little')
    return sign


def get_fragment_length(bytes_arg):
    return len(bytes_arg).to_bytes(4, byteorder='little')


# TODO - Now only used in ACK so we know how many fragments were mismatched
def get_number_of_fragments(number_of_fragments = 0):
    return number_of_fragments.to_bytes(2, byteorder='little')


def get_crc(data_in_bytes):
    nothing = 0
    if data_in_bytes == b'':
        return nothing.to_bytes(4, byteorder='little')
    crc_hex = calculate_crc(data_in_bytes)

    return int(crc_hex[2:], 16).to_bytes(4, byteorder='little')


def get_data(data_in_bytes, mismatch_simulation=False):
    message = data_in_bytes

    if type(data_in_bytes) is not bytes:
        message = data_in_bytes.encode(config.common['FORMAT']).strip()

    if mismatch_simulation and message != b'':
        message = message[:0] + 'E'.encode('utf-8') + message[0 + 1:]
        message = message[:1] + 'R'.encode('utf-8') + message[1 + 1:]
        message = message[:2] + 'R'.encode('utf-8') + message[2 + 1:]
        message = message[:3] + 'O'.encode('utf-8') + message[3 + 1:]
        message = message[:4] + 'R'.encode('utf-8') + message[4 + 1:]

    msg_length = len(message)
    send_length = str(msg_length).encode(config.common['FORMAT']).strip()
    send_length += b' ' * (config.header['HEADER_SIZE'] - len(send_length))

    return {'len': send_length, 'data': message}


def calculate_crc(data):
    crc32_func = crcmod.mkCrcFun(0x104c11db7, initCrc=0, xorOut=0xFFFFFFFF)
    result = hex(crc32_func(data))
    return result
