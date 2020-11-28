# GLOBAL
common = dict(
    FORMAT = 'utf-8'
)
# SIGNALS
signals = dict(
    CONNECTION_INITIALIZATION = 1,
    ACKNOWLEDGEMENT = 2,
    DATA_SENDING = 11, # TODO - nie je v dokumentacii, treba doplnit
)
# HEADER BASIC INFO - some of the properties are not used in all cases:
# addressing size might be smaller if user opts to send smaller fragments
header = dict(
    MAX_ADDRESSING_SIZE = 1500,
    MAX_ADDRESSING_SIZE_WITHOUT_HEADER = 1452, # TODO - should be 1456 but there are some 4 bytes in loopback idk what are these
    HEADER_SIZE = 14,
)
data = dict(
    BLOCK_SIZE = 15
)