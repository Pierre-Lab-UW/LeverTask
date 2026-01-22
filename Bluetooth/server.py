import socket
import os
import shutil
import subprocess

BASE_RX_DIR = "/tmp/bluetooth_rx"
OUTPUT_DIR = "/data/outputs"
BUFFER_SIZE = 1024

def recv_exact(sock, size):
    data = b""
    while len(data) < size:
        chunk = sock.recv(size - len(data))
        if not chunk:
            raise ConnectionError("Client disconnected")
        data += chunk
    return data

def recv_line(sock):
    buf = b""
    while b"\n" not in buf:
        chunk = sock.recv(256)
        if not chunk:
            raise ConnectionError("Client disconnected")
        buf += chunk
    return buf.partition(b"\n")[0].decode().strip()

def handle_send(sock, parts):
    _, _, training_id, filename, filesize = parts
    filesize = int(filesize)

    train_dir = os.path.join(BASE_RX_DIR, training_id)
    os.makedirs(train_dir, exist_ok=True)
    filepath = os.path.join(train_dir, os.path.basename(filename))

    sock.sendall(b"READY\n")
    data = recv_exact(sock, filesize)

    with open(filepath, "wb") as f:
        f.write(data)

    sock.sendall(b"OK\n")
    print("Received:", filepath)

def handle_request(sock, parts):
    _, _, filename = parts
    path = os.path.join(OUTPUT_DIR, os.path.basename(filename))

    if not os.path.isfile(path):
        sock.sendall(b"ERR\n")
        return

    size = os.path.getsize(path)
    sock.sendall(f"CMD SEND OUT {filename} {size}\n".encode())

    if recv_line(sock) != "READY":
        return

    with open(path, "rb") as f:
        shutil.copyfileobj(f, sock)

    print("Sent:", filename)

def handle_start(sock, parts):
    training_id = parts[2]
    path = os.path.join(BASE_RX_DIR, training_id)

    if not os.path.isdir(path) or not os.path.isfile(os.path.join(path, "GlobalParameters.yaml")) or not os.path.isfile(os.path.join(path, "RatioTraining.yaml")):
        sock.sendall(b"ERR\n")
        return

    subprocess.Popen([
        "sudo python3", "main.py",
        os.path.join(path, "GlobalParameters.yaml"),
        os.path.join(path, "RatioTraining.yaml")
    ])

    sock.sendall(b"OK\n")

def run_server(mac, channel):
    os.makedirs(BASE_RX_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    server = socket.socket(socket.AF_BLUETOOTH,
                           socket.SOCK_STREAM,
                           socket.BTPROTO_RFCOMM)
    server.bind((mac, channel))
    server.listen(1)

    print("Listening...")

    while True:
        client, addr = server.accept()
        print("Connected:", addr)

        try:
            while True:
                line = recv_line(client)
                parts = line.split()

                if parts[:2] == ["CMD", "SEND"]:
                    handle_send(client, parts)

                elif parts[:2] == ["CMD", "REQ"]:
                    handle_request(client, parts)

                elif parts[:2] == ["CMD", "START"]:
                    handle_start(client, parts)

                else:
                    client.sendall(b"ERR\n")

        except (ConnectionError, OSError) as e:
            print("Disconnected:", e)

        finally:
            client.close()

if __name__ == "__main__":
    run_server("B8:27:EB:7E:6F:9D", 4)
