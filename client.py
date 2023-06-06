import socket
import hashlib
import os
import math
import threading

HEADER = 64
FILE_DATA_SIZE=1024


DISCONNECT_MESSAGE = "!DISCONNECT"
NO_FILE_MESSAGE = "!NOFILE"
END_MESSAGE ="!END"
STARTING_SENDING_MESSAGE = "!START"

current_piece = 0
number_of_pieces = 0
undownloaded_pieces = []
successful_addresses = []
mutex = threading.Lock()
hashes = []

def request_piece(address, piece_length, piece_number):
    global undownloaded_pieces, hashes
    host, port, file_path = address
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))
    send(f"{file_path} {piece_length} {piece_number}", client)
    msg_length = client.recv(HEADER).decode()
    try:
        msg_length = int(msg_length)
    except:
        print(f"Invalid message from client: {host}")
        return
    msg = client.recv(msg_length).decode()
    if msg == NO_FILE_MESSAGE:
        send(DISCONNECT_MESSAGE, client)
        print(f"No file on: {host}")
        global undownloaded_pieces
        mutex.acquire()
        try:
            undownloaded_pieces.append(piece_number)
        finally:
            mutex.acquire()
    elif msg == STARTING_SENDING_MESSAGE:
        print(piece_number)
        get_chunk(f"p-{piece_number}.piece", client)
        if calculate_sha256(f"p-{piece_number}.piece") == hashes[piece_number]:
            print(f"Downloaded p-{piece_number}  from {host}")
            send(DISCONNECT_MESSAGE, client)
            global successful_addresses
            successful_addresses.append(address)
            get_piece_number(address, piece_length)
        else:
            send(DISCONNECT_MESSAGE, client)
            print(f"The hash function does not match on p-{piece_number} from {host}")
            mutex.acquire()
            try:
                undownloaded_pieces.append(piece_number)
            finally:
                mutex.acquire()
    else:
        mutex.acquire()
        try:
                undownloaded_pieces.append(piece_number)
        finally:
                mutex.acquire()
        print(f"Invalid message from {host}")
        raise Exception("Invalid message from client")


def get_piece_number(address, piece_length):
    global undownloaded_pieces, current_piece, number_of_pieces
    mutex.acquire()
    piece_number = -1
    try:
        if undownloaded_pieces:
            piece_number = undownloaded_pieces.pop()
        elif current_piece < number_of_pieces:
            piece_number = current_piece
            current_piece += 1
    finally:
        mutex.release()
        if piece_number > -1:
            request_piece(address, piece_length, piece_number)


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
    delete_pieces(pieces_number)

def delete_pieces(pieces_number):
    for i in range(pieces_number):
        file_name = f"p-{i}.piece"
        os.remove(file_name)

def download_file(addresses, file_size, piece_length, file_path, hash_list):
    global undownloaded_pieces, current_piece, number_of_pieces, successful_addresses, hashes
    undownloaded_pieces = []
    successful_addresses = []
    current_piece = 0
    number_of_pieces = math.ceil(file_size/piece_length)
    hashes = hash_list
    threads = []
    try:
        for address in addresses:
            thread = threading.Thread(target=get_piece_number, args=(address, piece_length))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

        while undownloaded_pieces:
            piece_number = undownloaded_pieces.pop()
            for address in successful_addresses:
                hash = hashes[piece_number]
                request_piece(address, piece_length, piece_number, hash)
                if piece_number not in undownloaded_pieces:
                    break
            if piece_number in undownloaded_pieces:
                raise Exception("File download failed")
        try:
            merge_to_file(number_of_pieces, file_path)
        except:
            print("Pieces merging failed")
    except:
        print("File download failed")

def calculate_hash_list(file_path, piece_length):
    hash_list = []
    with open(file_path, 'rb') as file:
            file_size = os.path.getsize(file_path)
            for _ in range(int(math.ceil(file_size/piece_length))):
                data = file.read(piece_length)
                hash_list.append(hashlib.sha256(data).hexdigest())
    return hash_list


# Przykład pobrania pliku
file_path = 'dowyslania/zdjecie.png'
host = socket.gethostbyname(socket.gethostname())
port = 5050

file_size = os.path.getsize(file_path)
piece_length = 65536
addresses = [('192.168.64.1', 5050, file_path)]
hash_list = calculate_hash_list(file_path, piece_length)
download_file(addresses, file_size, piece_length, "zdjecie.png", hash_list)