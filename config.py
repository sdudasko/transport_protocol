# GLOBAL
common = dict(
    FORMAT = 'utf-8'
)
# SIGNALS
signals = dict(
    CONNECTION_INITIALIZATION = 1,
    ACKNOWLEDGEMENT = 2,
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
    MAX_ADDRESSING_SIZE_WITHOUT_HEADER = 1454, # TODO - should be 1456 but there are some 4 bytes in loopback idk what are these
    HEADER_SIZE = 14,
)
data = dict(
    BLOCK_SIZE = 15
)