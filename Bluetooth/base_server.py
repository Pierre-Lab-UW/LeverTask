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
        self.running: bool = False
    
    def _recv_exact(self, sock: socket.socket, size: int) -> bytes:
        """Receive exact number of bytes."""
        data: bytes = b""
        while len(data) < size:
            chunk: bytes = sock.recv(size - len(data))
            if not chunk:
                raise ConnectionError("Client disconnected")
            data += chunk
        return data
    
    def _recv_line(self, sock: socket.socket) -> str:
        """Receive line (until newline)."""
        buf: bytes = b""
        while b"\n" not in buf:
            chunk: bytes = sock.recv(256)
            if not chunk:
                raise ConnectionError("Client disconnected")
            buf += chunk
        return buf.partition(b"\n")[0].decode().strip()
    
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
