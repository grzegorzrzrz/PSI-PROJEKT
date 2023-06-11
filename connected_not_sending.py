import socket

host = #swojeip
port = 5060

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port))
while True:
    pass