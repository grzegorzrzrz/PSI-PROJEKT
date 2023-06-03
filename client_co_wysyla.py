import socket
import threading
import os

HOST = socket.gethostbyname(socket.gethostname())
PORT = 5050
ADDR = (HOST, PORT)
HEADER = 64
DATA_SIZE=1024

DISCONNECT_MESSAGE = "!DISCONNECT"
NO_FILE_MESSAGE = "!NOFILE"
END_MESSAGE ="!END"
STARTING_SENDING_MESSAGE = "!START"

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.bind(ADDR)

def handle_file_request(conn, addr):
    print(f"New connection: {addr}")
    connected = True
    while connected:
        msg_length = conn.recv(HEADER).decode()
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode()
            if msg == DISCONNECT_MESSAGE:
                connected = False
            else:
                parts = msg.split()
                file_path = parts[0]
                piece_length = int(parts[1])
                piece_number = int(parts[2])
                if os.path.exists(file_path):
                    send(STARTING_SENDING_MESSAGE, conn)
                    send_piece(file_path, conn, piece_length, piece_number)
                else:
                    send(NO_FILE_MESSAGE, conn)
                    #TODO powiedz serwerowi ze nie masz pliku

            print(f"{addr} {msg}")

    conn.close()

def send(msg, client):
    message = msg.encode()
    msg_length = len(message)
    send_length = str(msg_length).encode()
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)

def send_binary(msg, client):
    msg_length = len(msg)
    send_length = str(msg_length).encode()
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(msg)


def send_piece(file_path, conn, piece_length, piece_number):
        with open(file_path, 'rb') as file:
            file.seek(piece_length*(piece_number))
            for _ in range(int(piece_length/DATA_SIZE)):
                data = file.read(DATA_SIZE)
                send_binary(data, conn)
                if len(data) != DATA_SIZE:
                    break
            print(f"end: {piece_number}")
            send(END_MESSAGE, conn)

def waiting_for_file_requests():
    client_socket.listen()
    while True:
        conn, addr = client_socket.accept()
        thread = threading.Thread(target=handle_file_request, args=(conn, addr))
        thread.start()
        print(f"Active threads: {threading.active_count()-1}")


file_path = 'dowyslania/zdjecie.png'
host = socket.gethostbyname(socket.gethostname())
port = 5050


print(f"Client starting on {ADDR}")
waiting_for_file_requests()