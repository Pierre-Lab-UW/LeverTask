import socket
import os
import shutil
import subprocess

BUFFER_SIZE = 1024

class BluetoothServer:
    """Manages Bluetooth RFCOMM server for receiving and executing training configs."""
    
    def __init__(self, mac, channel=4, rx_dir="/tmp/bluetooth_rx", output_dir="/data/outputs"):
        """Initialize Bluetooth server.
        
        Args:
            mac: MAC address to bind to
            channel: RFCOMM channel (default: 4)
            rx_dir: Directory for received files (default: /tmp/bluetooth_rx)
            output_dir: Directory for output files (default: /data/outputs)
        """
        self.mac = mac
        self.channel = channel
        self.rx_dir = rx_dir
        self.output_dir = output_dir
        self.server = None
        self.running = False
    
    def _recv_exact(self, sock, size):
        """Receive exact number of bytes."""
        data = b""
        while len(data) < size:
            chunk = sock.recv(size - len(data))
            if not chunk:
                raise ConnectionError("Client disconnected")
            data += chunk
        return data
    
    def _recv_line(self, sock):
        """Receive line (until newline)."""
        buf = b""
        while b"\n" not in buf:
            chunk = sock.recv(256)
            if not chunk:
                raise ConnectionError("Client disconnected")
            buf += chunk
        return buf.partition(b"\n")[0].decode().strip()
    
    def _handle_send(self, sock, parts):
        """Handle CMD SEND - receive file from client."""
        _, _, training_id, filename, filesize = parts
        filesize = int(filesize)

        train_dir = os.path.join(self.rx_dir, training_id)
        os.makedirs(train_dir, exist_ok=True)
        filepath = os.path.join(train_dir, os.path.basename(filename))

        sock.sendall(b"READY\n")
        data = self._recv_exact(sock, filesize)

        with open(filepath, "wb") as f:
            f.write(data)

        sock.sendall(b"OK\n")
        print("Received:", filepath)
    
    def _handle_request(self, sock, parts):
        """Handle CMD REQ - send output file to client."""
        _, _, filename = parts
        path = os.path.join(self.output_dir, os.path.basename(filename))

        if not os.path.isfile(path):
            sock.sendall(b"ERR\n")
            return

        size = os.path.getsize(path)
        sock.sendall(f"CMD SEND OUT {filename} {size}\n".encode())

        if self._recv_line(sock) != "READY":
            return

        with open(path, "rb") as f:
            shutil.copyfileobj(f, sock)

        print("Sent:", filename)
    
    def _handle_start(self, sock, parts):
        """Handle CMD START - start training on device."""
        training_id = parts[2]
        path = os.path.join(self.rx_dir, training_id)

        # Check if required files exist
        if (not os.path.isdir(path) or 
            not os.path.isfile(os.path.join(path, "GlobalParameters.yaml")) or 
            not os.path.isfile(os.path.join(path, "RatioTraining.yaml"))):
            sock.sendall(b"ERR\n")
            return

        # Start training process
        subprocess.Popen([
            "python3", "main.py",
            os.path.join(path, "GlobalParameters.yaml"),
            os.path.join(path, "RatioTraining.yaml")
        ])

        sock.sendall(b"OK\n")
    
    def _handle_client(self, client, addr):
        """Handle client connection."""
        print("Connected:", addr)
        try:
            while True:
                line = self._recv_line(client)
                parts = line.split()

                if parts[:2] == ["CMD", "SEND"]:
                    self._handle_send(client, parts)

                elif parts[:2] == ["CMD", "REQ"]:
                    self._handle_request(client, parts)

                elif parts[:2] == ["CMD", "START"]:
                    self._handle_start(client, parts)

                else:
                    client.sendall(b"ERR\n")

        except (ConnectionError, OSError) as e:
            print("Disconnected:", e)

        finally:
            client.close()
    
    def start(self):
        """Start the Bluetooth server."""
        os.makedirs(self.rx_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)

        self.server = socket.socket(socket.AF_BLUETOOTH,
                                   socket.SOCK_STREAM,
                                   socket.BTPROTO_RFCOMM)
        self.server.bind((self.mac, self.channel))
        self.server.listen(1)
        self.running = True

        print(f"Listening on {self.mac}:{self.channel}...")

        try:
            while self.running:
                client, addr = self.server.accept()
                self._handle_client(client, addr)
        except KeyboardInterrupt:
            print("Server shutting down...")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the Bluetooth server."""
        self.running = False
        if self.server:
            try:
                self.server.close()
            except:
                pass

def main():
    """Run Bluetooth server."""
    server = BluetoothServer("B8:27:EB:7E:6F:9D", channel=4)
    server.start()

if __name__ == "__main__":
    main()
