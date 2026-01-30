import socket
import os
from abc import ABC, abstractmethod
from typing import Optional, Tuple


class BluetoothServerBase(ABC):
    """Base class for Bluetooth RFCOMM servers. Handles socket communication logic."""
    
    def __init__(self, mac: str, channel: int = 4) -> None:
        """Initialize Bluetooth server.
        
        Args:
            mac: MAC address to bind to
            channel: RFCOMM channel (default: 4)
        """
        self.mac: str = mac
        self.channel: int = channel
        self.server: Optional[socket.socket] = None
        self.sock: Optional[socket.socket] = None  # Current client socket
        self.running: bool = False
    
    def recv_exact(self, size: int) -> bytes:
        """Receive exact number of bytes from client socket."""
        data: bytes = b""
        while len(data) < size:
            chunk: bytes = self.sock.recv(size - len(data))
            if not chunk:
                raise ConnectionError("Client disconnected")
            data += chunk
        return data
    
    def recv_line(self) -> str:
        """Receive line (until newline) from client socket."""
        buf: bytes = b""
        while b"\n" not in buf:
            chunk: bytes = self.sock.recv(256)
            if not chunk:
                raise ConnectionError("Client disconnected")
            buf += chunk
        return buf.partition(b"\n")[0].decode().strip()
    
    def send_bytes(self, data: bytes) -> None:
        """Send raw bytes to client.
        
        Args:
            data: Bytes to send
        """
        self.sock.sendall(data)
    
    def send_message(self, message: str) -> None:
        """Send text message to client with newline.
        
        Args:
            message: Message to send
        """
        self.sock.sendall(message.encode() + b"\n")
    
    def send_file_content(self, file_path: str) -> None:
        """Send file content to client in chunks.
        
        Args:
            file_path: Path to file to send
        """
        with open(file_path, "rb") as f:
            while chunk := f.read(1024):
                self.sock.sendall(chunk)
    
    def save_received_file(self, file_path: str, size: int) -> None:
        """Save received bytes from client to file.
        
        Args:
            file_path: Path where to save file
            size: Number of bytes to receive
        """
        data: bytes = self.recv_exact(size)
        with open(file_path, "wb") as f:
            f.write(data)
    
    @abstractmethod
    def _handle_client(self, client: socket.socket, addr: Tuple[str, int]) -> None:
        """Handle client connection. Must be implemented by subclass.
        
        Args:
            client: Client socket
            addr: Client address
        """
        pass
    
    def start(self) -> None:
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
    
    def stop(self) -> None:
        """Stop the Bluetooth server."""
        self.running = False
        if self.server:
            try:
                self.server.close()
            except:
                pass
