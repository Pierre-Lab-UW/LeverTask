import socket
import os
from abc import ABC, abstractmethod

BUFFER_SIZE = 1024

class BluetoothServerBase(ABC):
    """Base class for Bluetooth RFCOMM servers. Handles socket communication logic."""
    
    def __init__(self, mac, channel=4):
        """Initialize Bluetooth server.
        
        Args:
            mac: MAC address to bind to
            channel: RFCOMM channel (default: 4)
        """
        self.mac = mac
        self.channel = channel
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
    
    @abstractmethod
    def _handle_client(self, client, addr):
        """Handle client connection. Must be implemented by subclass.
        
        Args:
            client: Client socket
            addr: Client address
        """
        pass
    
    def start(self):
        """Start the Bluetooth server."""
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
