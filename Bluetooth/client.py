# import socket

# client = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
# client.connect(("", 4))  # Replace with server MAC address and port

# try:
#     while True:
#         message = input("Enter message to send: ")
#         if message.lower() == "quit":
#             break
#         client.sendall(message.encode())
#         data = client.recv(1024)
#         print("Received:", data.decode())
# except OSError as e:
#     print("Connection error:", e)
import socket
import os

BUFFER_SIZE = 1024

def recv_line(sock):
    """Receive until newline"""
    data = b""
    while True:
        chunk = sock.recv(1)
        if not chunk:
            raise ConnectionError("Connection closed")
        if chunk == b"\n":
            break
        data += chunk
    return data.decode().strip()


def send_file(sock, training_id, filepath):
    if not os.path.isfile(filepath):
        print("File does not exist:", filepath)
        return

    filename = os.path.basename(filepath)
    filesize = os.path.getsize(filepath)

    # Send header
    header = f"CMD SEND {training_id} {filename} {filesize}\n"
    sock.sendall(header.encode())

    print(f"Sending file {filename} ({filesize} bytes)...")

    with open(filepath, "rb") as f:
        while True:
            chunk = f.read(BUFFER_SIZE)
            if not chunk:
                break
            sock.sendall(chunk)

    # Wait for acknowledgment
    resp = recv_line(sock)
    print("PI response:", resp)


def request_file(sock, filename, save_path):
    sock.sendall(f"CMD REQ {filename}\n".encode())

    header = recv_line(sock)
    parts = header.split()

    if parts[:2] != ["CMD", "SEND"]:
        print("Failed to request file:", header)
        return

    filesize = int(parts[4])
    print(f"Receiving file {filename} ({filesize} bytes)...")

    received = 0
    with open(save_path, "wb") as f:
        while received < filesize:
            chunk = sock.recv(min(BUFFER_SIZE, filesize - received))
            if not chunk:
                raise ConnectionError("Connection lost")
            f.write(chunk)
            received += len(chunk)

    print(f"File saved to {save_path}")


def main():
    server_mac = input("Enter Bluetooth MAC address: ").strip()
    channel = int(input("Enter RFCOMM channel (e.g., 4): "))

    client = socket.socket(
        socket.AF_BLUETOOTH,
        socket.SOCK_STREAM,
        socket.BTPROTO_RFCOMM
    )

    try:
        client.connect((server_mac, channel))
    except OSError as e:
        print("Failed to connect:", e)
        return

    print("Connected. Enter commands:")
    print("  send <training_id> <file_path>")
    print("  request <filename> <save_path>")
    print("  start <training_id>")
    print("  quit")

    try:
        while True:
            cmd = input("> ").strip()
            if not cmd:
                continue

            parts = cmd.split()

            if parts[0].lower() == "send" and len(parts) == 3:
                send_file(client, parts[1], parts[2])

            elif parts[0].lower() == "request" and len(parts) == 3:
                request_file(client, parts[1], parts[2])

            elif parts[0].lower() == "start" and len(parts) == 2:
                client.sendall(f"CMD START {parts[1]}\n".encode())

            elif parts[0].lower() == "quit":
                break

            else:
                print("Unknown command or wrong number of arguments.")

    except (OSError, ConnectionError) as e:
        print("Connection error:", e)

    finally:
        client.close()
        print("Disconnected.")


if __name__ == "__main__":
    main()
