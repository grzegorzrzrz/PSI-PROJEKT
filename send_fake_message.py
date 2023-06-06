import socket

host = socket.gethostbyname(socket.gethostname())
port = 5050

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port))
client.send("      ".encode())