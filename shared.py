import config

def get_max_size_of_receiving_packet():  # TODO - toto si musi vediet uzivatel navolit, zatial dajme max, co moze byt
    return 1500


def get_max_size_of_receiving_packet_without_header():  # TODO - toto si musi vediet uzivatel navolit, zatial dajme max, co moze byt
    return 1456


def get_fragment_order():
    return 0


def get_signal_message(signal):
    return config.signals[signal]


def get_fragment_length():
    return 0


def get_crc():
    return 0


def get_data():
    return b''
