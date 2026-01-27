import socket
import os

BUFFER_SIZE = 1024

class BluetoothClient:
    """Manages Bluetooth RFCOMM connection and communication."""
    
    def __init__(self, mac, channel=1, timeout=10):
        """Initialize Bluetooth client.
        
        Args:
            mac: MAC address of device
            channel: RFCOMM channel (default: 1)
            timeout: Socket timeout in seconds (default: 10)
        """
        self.mac = mac
        self.channel = channel
        self.timeout = timeout
        self.sock = None
        self.connected = False
    
    def connect(self):
        """Connect to Bluetooth device."""
        try:
            self.sock = socket.socket(socket.AF_BLUETOOTH,
                                     socket.SOCK_STREAM,
                                     socket.BTPROTO_RFCOMM)
            self.sock.settimeout(self.timeout)
            self.sock.connect((self.mac, self.channel))
            self.connected = True
            return True
        except Exception as e:
            self.connected = False
            raise ConnectionError(f"Failed to connect to {self.mac}: {str(e)}")
    
    def disconnect(self):
        """Disconnect from device."""
        if self.sock:
            try:
                self.sock.close()
            except:
                pass
            self.connected = False
    
    def recv_exact(self, size):
        """Receive exact number of bytes."""
        data = b""
        while len(data) < size:
            chunk = self.sock.recv(size - len(data))
            if not chunk:
                raise ConnectionError("Connection lost")
            data += chunk
        return data
    
    def recv_line(self):
        """Receive line (until newline)."""
        buf = b""
        while b"\n" not in buf:
            chunk = self.sock.recv(256)
            if not chunk:
                raise ConnectionError("Connection closed")
            buf += chunk
        return buf.partition(b"\n")[0].decode().strip()
    
    def send_file(self, training_id, path):
        """Send file to device.
        
        Args:
            training_id: Training identifier
            path: Path to file to send
            
        Returns:
            Server response message
        """
        if not self.connected:
            raise RuntimeError("Not connected to device")
        
        filename = os.path.basename(path)
        filesize = os.path.getsize(path)

        self.sock.sendall(f"CMD SEND {training_id} {filename} {filesize}\n".encode())
        resp = self.recv_line()
        if resp != "READY":
            raise RuntimeError(f"Server not ready: {resp}")

        with open(path, "rb") as f:
            while chunk := f.read(BUFFER_SIZE):
                self.sock.sendall(chunk)

        return self.recv_line()
    
    def request_file(self, filename, save_path):
        """Request file from device.
        
        Args:
            filename: Name of file to request
            save_path: Path where to save received file
        """
        if not self.connected:
            raise RuntimeError("Not connected to device")
        
        self.sock.sendall(f"CMD REQ {filename}\n".encode())

        header = self.recv_line()
        parts = header.split()
        if parts[:3] != ["CMD", "SEND", "OUT"]:
            raise RuntimeError(f"Invalid server response: {header}")

        filesize = int(parts[4])
        self.sock.sendall(b"READY\n")

        data = self.recv_exact(filesize)
        with open(save_path, "wb") as f:
            f.write(data)
    
    def start_training(self, training_id):
        """Start training on device.
        
        Args:
            training_id: Training identifier
            
        Returns:
            Server response message
        """
        if not self.connected:
            raise RuntimeError("Not connected to device")
        
        self.sock.sendall(f"CMD START {training_id}\n".encode())
        return self.recv_line()

def main():
    """Interactive CLI for Bluetooth client."""
    mac = input("MAC: ").strip()
    channel = int(input("Channel: "))

    client = BluetoothClient(mac, channel)
    
    try:
        client.connect()
        print(f"Connected to {mac}")
        
        while True:
            cmd = input("> ").strip().split()
            if not cmd:
                continue

            try:
                if cmd[0] == "send" and len(cmd) == 3:
                    resp = client.send_file(cmd[1], cmd[2])
                    print("Server:", resp)

                elif cmd[0] == "request" and len(cmd) == 3:
                    client.request_file(cmd[1], cmd[2])
                    print("File received:", cmd[2])

                elif cmd[0] == "start" and len(cmd) == 2:
                    resp = client.start_training(cmd[1])
                    print("Server:", resp)

                elif cmd[0] == "quit":
                    break
                
                else:
                    print("Unknown command")
            
            except Exception as e:
                print(f"Error: {str(e)}")
    
    finally:
        client.disconnect()

if __name__ == "__main__":
    main()
