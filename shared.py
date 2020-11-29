import config


def get_max_size_of_receiving_packet():  # TODO - toto si musi vediet uzivatel navolit, zatial dajme max, co moze byt
    return 1500


def get_max_size_of_receiving_packet_without_header():  # TODO - toto si musi vediet uzivatel navolit, zatial dajme max, co moze byt
    return 1456


def get_fragment_order(order):
    order = order.to_bytes(2, byteorder='little')
    return order


def get_signal_message(signal):
    print(f"Sign: {signal}")
    sign = config.signals[signal].to_bytes(2, byteorder='little')
    return sign


def get_fragment_length(bytes_arg):
    return len(bytes_arg).to_bytes(4, byteorder='little')


def get_number_of_fragments():
    abc = 19 # TODO
    return abc.to_bytes(2, byteorder='little')


def get_crc():
    abc = 15 # TODO
    return abc.to_bytes(4, byteorder='little')


def get_data(data_in_bytes):
    message = data_in_bytes
    if type(data_in_bytes) is not bytes:
        message = data_in_bytes.encode(config.common['FORMAT']).strip()

    msg_length = len(message)
    send_length = str(msg_length).encode(config.common['FORMAT']).strip()
    send_length += b' ' * (config.header['HEADER_SIZE'] - len(send_length))

    return {'len': send_length, 'data': message}
