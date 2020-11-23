import socket

HEADER = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
ADDR = (SERVER, PORT) # on tam mal "localhost", 12345

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)  # We are connecting to the server

# client.sendto("ahoj".encode(), ADDR)
# client.recvfrom(1000)

def send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)

    send_length += b' ' * (HEADER - len(send_length))
    print(send_length)
    client.send(send_length)

    client.send(message)


send("Hello World!")
send("Hello Joshua!")
send("Hello Willy Wonka!")
send(DISCONNECT_MESSAGE)
