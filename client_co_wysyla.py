import socket
import threading
import os
import requests

HOST = socket.gethostbyname(socket.gethostname())
PORT = 5060
ADDR = (HOST, PORT)
HEADER = 64
DATA_SIZE=1024
PIECE_LENGTH= 65536

DISCONNECT_MESSAGE = "!DISCONNECT"
NO_FILE_MESSAGE = "!NOFILE"
END_MESSAGE ="!END"
STARTING_SENDING_MESSAGE = "!START"


def handle_file_request(conn, addr):
    conn.settimeout(10)
    print(f"New connection: {addr}")
    try:
        connected = True
        while connected:
            msg_length = conn.recv(HEADER).decode()
            if msg_length:
                try:
                    msg_length = int(msg_length)
                    msg = conn.recv(msg_length).decode()
                    if msg == DISCONNECT_MESSAGE:
                        connected = False
                    else:
                        parts = msg.split()
                        try:
                            file_path = parts[0]
                            piece_length = int(parts[1])
                            piece_number = int(parts[2])
                            id = int(parts[3])
                            if os.path.exists(file_path):
                                send(STARTING_SENDING_MESSAGE, conn)
                                send_piece(file_path, conn, piece_length, piece_number)
                            else:
                                send(NO_FILE_MESSAGE, conn)
                                data1 = {'ip': str(ADDR), 'file_id': id}
                                response = requests.patch("http://localhost:3000/seeders", json=data1)
                        except:
                            print(f"Invalid message from {addr}")
                            break
                    print(f"{addr} {msg}")
                except:
                    print(f"Invalid message from {addr}")
                    break
    except socket.error:
        print(f"Waited too long for an answer from {addr}")
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
            send(END_MESSAGE, conn)

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.bind(ADDR)

def waiting_for_file_requests():
    client_socket.listen()
    while True:
        conn, addr = client_socket.accept()
        thread = threading.Thread(target=handle_file_request, args=(conn, addr))
        thread.start()
        print(f"Active threads: {threading.active_count()-1}")


print(f"Client starting on {ADDR}")
waiting_for_file_requests()
