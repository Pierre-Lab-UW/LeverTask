import bluetooth
import os
import shutil

class BluetoothReceiver:
    PORT = bluetooth.PORT_ANY
    BACKLOG = 1
    BUFFER_SIZE = 1024

    BASE_RX_DIR = "/tmp/bluetooth_rx"
    OUTPUT_DIR = "/data/outputs"

    def __init__(self):
        pass

    def safe_recv(self, sock, size):
        """Receive exactly size bytes"""
        data = b""
        while len(data) < size:
            chunk = sock.recv(min(self.BUFFER_SIZE, size - len(data)))
            if not chunk:
                raise ConnectionError("Client disconnected during transfer")
            data += chunk
        return data


    def handle_send(self, sock, parts):

        if not self.should_recieve_file():
            sock.sendall(b"ERR_BUSY\n")
            return

        _, _, training_id, filename, filesize = parts
        filesize = int(filesize)

        # Security: filename only
        filename = os.path.basename(filename)

        train_dir = os.path.join(self.BASE_RX_DIR, training_id)
        os.makedirs(train_dir, exist_ok=True)

        filepath = os.path.join(train_dir, filename)

        print(f"Receiving file {filename} ({filesize} bytes)")

        with open(filepath, "wb") as f:
            f.write(self.safe_recv(sock, filesize))

        sock.sendall(b"SUCCESS\n")
        print("File received:", filepath)

        # Example: update global config here
        # update_config(filepath)

        # Start training (placeholder)


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

    def should_recieve_file(self) -> bool:
        return True

    def run_server(self):
        server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        server_sock.bind(("", self.PORT))
        server_sock.listen(self.BACKLOG)

        port = server_sock.getsockname()[1]

        bluetooth.advertise_service(
            server_sock,
            "BluetoothFileReceiver",
            service_classes=[bluetooth.SERIAL_PORT_CLASS],
            profiles=[bluetooth.SERIAL_PORT_PROFILE],
        )

        print(f"Listening on RFCOMM channel {port}")

        while True:
            print("Waiting for connection...")
            client_sock, client_info = server_sock.accept()
            print(f"Connected to {client_info}")

            try:
                buffer = b""
                while True:
                    buffer += client_sock.recv(self.BUFFER_SIZE)
                    if not buffer:
                        break

                    while b"\n" in buffer:
                        line, buffer = buffer.split(b"\n", 1)
                        parts = line.decode().strip().split()

                        if parts[:2] == ["CMD", "SEND"]:
                            self.handle_send(client_sock, parts)

                        elif parts[:2] == ["CMD", "REQ"]:
                            self.handle_request(client_sock, parts)

                        elif parts == ["CMD", "DONE"]:
                            self.state = self.STATE_IDLE
                            print("Training complete")
                            client_sock.sendall(b"SUCCESS\n")

                        else:
                            client_sock.sendall(b"FAIL\n")

            except Exception as e:
                print("Connection error:", e)

            finally:
                client_sock.close()
                print("Connection closed\n")


if __name__ == "__main__":
    os.makedirs(BluetoothReceiver.BASE_RX_DIR, exist_ok=True)
    os.makedirs(BluetoothReceiver.OUTPUT_DIR, exist_ok=True)

    reciever = BluetoothReceiver()
    reciever.run_server()
