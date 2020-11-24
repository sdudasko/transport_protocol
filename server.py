import socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = (socket.gethostname(), 1234)
client_socket = (socket.gethostname(), 1235)

server_socket.bind(server_address)

while True:
    data, address = server_socket.recvfrom(4096)

    msg = "Welcome to the server!"
    msg = f'{len(msg):<20}' + msg

    client_socket = server_socket.sendto(b"Vitaj na server!:)", address)
    print(data)
    print(address)
    print(client_socket)


