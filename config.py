# GLOBAL
common = dict(
    FORMAT = 'utf-8',
    DISCONNECT_AFTER_N_SECONDS = 60,
    SIMULACIA_CHYBY_VO_FRAGMENTE = 1
)
# SIGNALS
signals = dict(
    CONNECTION_INITIALIZATION = 1,
    ACKNOWLEDGEMENT = 2,
    CONNECTION_CLOSE_REQUEST = 3,
    CONNECTION_CLOSE_ACK = 4,
    KEEP_ALIVE = 5,
    FRAGMENT_ACK_OK = 6,
    FRAGMENT_ACK_CRC_MISMATCH = 7,
    FILENAME = 9,
    STDIN = 10,
    DATA_SENDING = 11, # TODO - nie je v dokumentacii, treba doplnit
    KEEP_ALIVE_ACK = 12, # TODO - nie je v dokumentacii, treba doplnit
)
# HEADER BASIC INFO - some of the properties are not used in all cases:
# addressing size might be smaller if user opts to send smaller fragments
header = dict(
    MAX_ADDRESSING_SIZE = 1500,
    MAX_ADDRESSING_SIZE_WITHOUT_HEADER = 1454,
    HEADER_SIZE = 14,
)
data = dict(
    BLOCK_SIZE = 15
)