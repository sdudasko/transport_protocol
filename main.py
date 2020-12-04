import server
import client
import threading

def sw_sides(i_want_to_be="client"):
    switch_sides = 'Do you want to switch sides?'
    switch_sides_bool = input("%s (y/N) " % switch_sides).lower() == 'y'

    if switch_sides_bool:
        server.server_close()
        client.client_close()

        if i_want_to_be == "client":
            client.client_behaviour(1238)
        else:
            server.server_behaviour(1237)


def get_input():
    while True:
        sw_sides()



msg = 'Chces byt server?'
server_opt = input("%s (y/N) " % msg).lower() == 'y'

while True:
    if server_opt:
        input_thread = threading.Thread(target=get_input)
        input_thread.start()
        server.server_behaviour()
    else:
        client.client_behaviour()
        sw_sides("server")


