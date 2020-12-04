import server
import client

msg = 'Chces byt server?'
server_opt = input("%s (y/N) " % msg).lower() == 'y'

if server_opt:
    server.server_behaviour()
else:
    client.client_behaviour()