import socket
import threading

HEADER = 64  # No matter how big the message is, it has to be 64, if we sent 5B message, it is 5MB + 61MB offset
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # af_inet stands for ipv4
server.bind(ADDR)

# data, clientaddr = server.recvfrom(1000) # 1000B vie prijat, vracia data a klientovu adresu
# print(data)
# print(clientaddr) # Vidime, z akeho portu to posiela
# server.sendto("cau".encode(), clientaddr)

# server.close()

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")

    connected = True
    while connected:
        msg_length = conn.recv(HEADER).decode(FORMAT)

        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)
            if msg == DISCONNECT_MESSAGE:
                connected = False

            print(f"[{addr}] {msg}")
            conn.send("Msg received".encode(FORMAT))

    conn.close()


def start():
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")


print("[STARTING] server is starting...")
start()

if __name__ == '__main__':
    print("cau")
