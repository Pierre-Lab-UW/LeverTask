import socket
import os

BUFFER_SIZE = 1024

def recv_exact(sock, size):
    data = b""
    while len(data) < size:
        chunk = sock.recv(size - len(data))
        if not chunk:
            raise ConnectionError("Connection lost")
        data += chunk
    return data

def recv_line(sock):
    buf = b""
    while b"\n" not in buf:
        chunk = sock.recv(256)
        if not chunk:
            raise ConnectionError("Connection closed")
        buf += chunk
    return buf.partition(b"\n")[0].decode().strip()

def send_file(sock, training_id, path):
    filename = os.path.basename(path)
    filesize = os.path.getsize(path)

    sock.sendall(f"CMD SEND {training_id} {filename} {filesize}\n".encode())
    resp = recv_line(sock)
    if resp != "READY":
        raise RuntimeError(f"Server not ready: {resp}")

    with open(path, "rb") as f:
        while chunk := f.read(BUFFER_SIZE):
            sock.sendall(chunk)

    print("Server:", recv_line(sock))

def request_file(sock, filename, save_path):
    sock.sendall(f"CMD REQ {filename}\n".encode())

    header = recv_line(sock)
    parts = header.split()
    if parts[:3] != ["CMD", "SEND", "OUT"]:
        raise RuntimeError(header)

    filesize = int(parts[4])
    sock.sendall(b"READY\n")

    data = recv_exact(sock, filesize)
    with open(save_path, "wb") as f:
        f.write(data)

    print("File received:", save_path)

def main():
    mac = input("MAC: ").strip()
    channel = int(input("Channel: "))

    sock = socket.socket(socket.AF_BLUETOOTH,
                         socket.SOCK_STREAM,
                         socket.BTPROTO_RFCOMM)
    sock.settimeout(10)
    sock.connect((mac, channel))

    while True:
        cmd = input("> ").strip().split()
        if not cmd:
            continue

        if cmd[0] == "send" and len(cmd) == 3:
            send_file(sock, cmd[1], cmd[2])

        elif cmd[0] == "request" and len(cmd) == 3:
            request_file(sock, cmd[1], cmd[2])

        elif cmd[0] == "start" and len(cmd) == 2:
            sock.sendall(f"CMD START {cmd[1]}\n".encode())
            print(recv_line(sock))

        elif cmd[0] == "quit":
            break

    sock.close()

if __name__ == "__main__":
    main()
