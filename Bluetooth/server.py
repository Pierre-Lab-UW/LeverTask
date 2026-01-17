# import socket

# server = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
# server.bind(("B8:27:EB:7E:6F:9D", 4))
# server.listen(1)

# client, address = server.accept()

# try:
#     while True:
#         data = client.recv(1024)
#         if not data:
#             break
#         print("Received:", data.decode())
#         message = input("Enter message to send: ")
#         client.sendall(message.encode())
# except OSError as e:
#     print("Connection error:", e)
import socket
import os
import shutil
import subprocess
import time

class BluetoothReceiver:
    BUFFER_SIZE = 1024

    BASE_RX_DIR = "/tmp/bluetooth_rx"
    OUTPUT_DIR = "/data/outputs"

    def __init__(self, mac_addr, channel):
        self.mac_addr = mac_addr
        self.channel = channel

    def safe_recv(self, sock, size, timeout=10.0):
        """
        Receive exactly `size` bytes or raise TimeoutError.
        timeout = max total seconds allowed for the transfer
        """
        sock.settimeout(1.0)  # short recv timeout so we can check elapsed time
        data = b""
        start = time.monotonic()

        while len(data) < size:
            if time.monotonic() - start > timeout:
                raise TimeoutError("safe_recv timed out: "+str(len(data))+"/"+str(size)+" bytes received")

            try:
                chunk = sock.recv(min(self.BUFFER_SIZE, size - len(data)))
                if not chunk:
                    raise ConnectionError("Client disconnected during transfer")
                data += chunk
            except socket.timeout:
                continue  # keep looping until total timeout expires

        return data


    def recv_line(self, sock):
        """Receive until newline"""
        data = b""
        while True:
            chunk = sock.recv(1)
            if not chunk:
                raise ConnectionError("Client disconnected")
            if chunk == b"\n":
                break
            data += chunk
        return data.decode().strip()

    def should_recieve_file(self) -> bool:
        return True

    def handle_send(self, sock, parts):
        if not self.should_recieve_file():
            sock.sendall(b"ERR_BUSY\n")
            return

        _, _, training_id, filename, filesize = parts
        filesize = int(filesize)

        filename = os.path.basename(filename)
        train_dir = os.path.join(self.BASE_RX_DIR, training_id)
        os.makedirs(train_dir, exist_ok=True)

        filepath = os.path.join(train_dir, filename)
        print(f"Receiving file {filename} ({filesize} bytes)")

        with open(filepath, "wb") as f:
            f.write(self.safe_recv(sock, filesize))

        sock.sendall(b"SUCCESS\n")
        print("File received:", filepath)

    def handle_request(self, sock, parts):
        _, _, filename = parts
        filename = os.path.basename(filename)

        filepath = os.path.join(self.OUTPUT_DIR, filename)

        if not os.path.isfile(filepath):
            sock.sendall(b"FAIL\n")
            return

        filesize = os.path.getsize(filepath)
        sock.sendall(f"CMD SEND OUT {filename} {filesize}\n".encode())

        with open(filepath, "rb") as f:
            shutil.copyfileobj(f, sock)

        print("Output file sent:", filename)

    def handle_start(self, sock, parts):
        if len(parts) < 3:
            sock.sendall(b"ERROR: No training id sent!\n")
            return

        training_id = parts[2]
        training_path = os.path.join(self.BASE_RX_DIR, training_id)

        if not os.path.isdir(training_path):
            sock.sendall(f"ERROR: Invalid Training ID {training_id}!\n".encode())
            return

        subprocess.Popen([
            "lxterminal", "--command",
            f"python3 main.py "
            f"{os.path.join(training_path, 'GlobalParameters.yaml')} "
            f"{os.path.join(training_path, 'RatioTraining.yaml')}"
        ])

        sock.sendall(b"Training Successfully Started!\n")

    def run_server(self):
        server = socket.socket(
            socket.AF_BLUETOOTH,
            socket.SOCK_STREAM,
            socket.BTPROTO_RFCOMM
        )

        server.bind((self.mac_addr, self.channel))
        server.listen(1)

        print(f"Listening on {self.mac_addr} RFCOMM channel {self.channel}")

        while True:
            print("Waiting for connection...")
            client, address = server.accept()
            print("Connected:", address)

            try:
                while True:
                    line = self.recv_line(client)
                    print("Received command:", line)
                    parts = line.split()

                    if parts[:2] == ["CMD", "SEND"]:
                        self.handle_send(client, parts)

                    elif parts[:2] == ["CMD", "REQ"]:
                        self.handle_request(client, parts)

                    elif parts[:2] == ["CMD", "START"]:
                        self.handle_start(client, parts)

                    elif parts == ["CMD", "DONE"]:
                        client.sendall(b"SUCCESS\n")

                    else:
                        client.sendall(b"FAIL\n")

            except (OSError, ConnectionError) as e:
                print("Connection error:", e)

            finally:
                client.close()
                print("Connection closed\n")


if __name__ == "__main__":
    os.makedirs(BluetoothReceiver.BASE_RX_DIR, exist_ok=True)
    os.makedirs(BluetoothReceiver.OUTPUT_DIR, exist_ok=True)

    # Replace with Pi MAC + RFCOMM channel
    receiver = BluetoothReceiver("B8:27:EB:7E:6F:9D", 4)
    receiver.run_server()
