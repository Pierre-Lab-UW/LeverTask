import socket

client = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
client.connect(("B8:27:EB:7E:6F:9D", 4))  # Replace with server MAC address and port

try:
    while True:
        message = input("Enter message to send: ")
        if message.lower() == "quit":
            break
        client.sendall(message.encode())
        data = client.recv(1024)
        print("Received:", data.decode())
except OSError as e:
    print("Connection error:", e)