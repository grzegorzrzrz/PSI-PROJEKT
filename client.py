import socket
import hashlib
import os
import math

HEADER = 64
FILE_DATA_SIZE=1024


DISCONNECT_MESSAGE = "!DISCONNECT"
NO_FILE_MESSAGE = "!NOFILE"
END_MESSAGE ="!END"
STARTING_SENDING_MESSAGE = "!START"

def request_piece(file_path, host, port, piece_length, piece_number):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))
    send(f"{file_path} {piece_length} {piece_number}", client)
    msg_length = client.recv(HEADER).decode()
    msg_length = int(msg_length)
    msg = client.recv(msg_length).decode()
    if msg == NO_FILE_MESSAGE:
        send(DISCONNECT_MESSAGE, client)
    elif msg == STARTING_SENDING_MESSAGE:
        get_chunk(f"p-{piece_number}.piece", client)
        #TODO sprawdzenie czy funkcja skrotu sie zgadza
        print(calculate_sha256(f"p-{piece_number}.piece"))
        send(DISCONNECT_MESSAGE, client)


def get_chunk(piece_name, client):
     with open(piece_name, 'wb') as file:
            msg_length = client.recv(HEADER).decode()
            msg_length = int(msg_length)
            data = client.recv(msg_length)
            while data:
                if len(data) == len(END_MESSAGE.encode()):
                    if data.decode() == END_MESSAGE:
                        break
                file.write(data)
                msg_length = client.recv(HEADER).decode()
                msg_length = int(msg_length)
                data = client.recv(msg_length)

def calculate_sha256(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, 'rb') as file:
        for chunk in iter(lambda: file.read(4096), b''):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()


def send(msg, client):
    message = msg.encode()
    msg_length = len(message)
    send_length = str(msg_length).encode()
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)

def merge_to_file(pieces_number, output_file):
    with open(output_file, 'wb') as output:
        for i in range(pieces_number):
            file_name = f"p-{i}.piece"
            with open(file_name, 'rb') as file:
                output.write(file.read())
    #delete_pieces(pieces_number)

def delete_pieces(pieces_number):
    for i in range(pieces_number):
        file_name = f"p-{i}.piece"
        os.remove(file_name)


# Przykład pobrania pliku
file_path = 'dowyslania/zdjecie.png'
host = socket.gethostbyname(socket.gethostname())
port = 5050

file_size = os.path.getsize(file_path)
piece_length = 65536
number_of_pieces = math.ceil(file_size/piece_length)
for i in range(int(number_of_pieces)):
    request_piece(file_path, '192.168.64.1', 5050, piece_length, i)

merge_to_file(number_of_pieces, "zdjecie.png")