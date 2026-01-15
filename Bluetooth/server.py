import socket

server = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
server.bind(("B8:27:EB:7E:6F:9D", 4))
server.listen(1)

client, address = server.accept()

try:
    while True:
        data = client.recv(1024)
        if not data:
            break
        print("Received:", data.decode())
        message = input("Enter message to send: ")
        client.sendall(message.encode())
except OSError as e:
    print("Connection error:", e)
    