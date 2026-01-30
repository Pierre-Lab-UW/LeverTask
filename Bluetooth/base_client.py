import socket
from abc import ABC, abstractmethod
from typing import Optional

BUFFER_SIZE: int = 1024

class BluetoothClientBase(ABC):
    """Base class for Bluetooth RFCOMM clients. Handles socket communication logic."""
    
    def __init__(self, mac: str, channel: int = 1, timeout: int = 10) -> None:
        """Initialize Bluetooth client.
        
        Args:
            mac: MAC address of device
            channel: RFCOMM channel (default: 1)
            timeout: Socket timeout in seconds (default: 10)
        """
        self.mac: str = mac
        self.channel: int = channel
        self.timeout: int = timeout
        self.sock: Optional[socket.socket] = None
        self.connected: bool = False
    
    def connect(self) -> bool:
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
    
    def disconnect(self) -> None:
        """Disconnect from device."""
        if self.sock:
            try:
                self.sock.close()
            except:
                pass
            self.connected = False
    
    def _recv_exact(self, size: int) -> bytes:
        """Receive exact number of bytes."""
        data: bytes = b""
        while len(data) < size:
            chunk: bytes = self.sock.recv(size - len(data))
            if not chunk:
                raise ConnectionError("Connection lost")
            data += chunk
        return data
    
    def _recv_line(self) -> str:
        """Receive line (until newline)."""
        buf: bytes = b""
        while b"\n" not in buf:
            chunk: bytes = self.sock.recv(256)
            if not chunk:
                raise ConnectionError("Connection closed")
            buf += chunk
        return buf.partition(b"\n")[0].decode().strip()
    
    def _send_command(self, command: str) -> None:
        """Send command to device.
        
        Args:
            command: Command string to send
        """
        if not self.connected:
            raise RuntimeError("Not connected to device")
        self.sock.sendall(command.encode() + b"\n")
