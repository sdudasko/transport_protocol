import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = (socket.gethostname(), 1234)
client_address = (socket.gethostname(), 1235)

# sock.bind(client_address)

message = b"mm"

# Send data
sent = client_socket.sendto(message, server_address)

while True:
    # Receive response
    data, server = client_socket.recvfrom(4096) #Value when to stop reading
    print(data)

