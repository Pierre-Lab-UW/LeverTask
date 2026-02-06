import socket
from abc import ABC, abstractmethod
from typing import Optional
import select

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
    
    def recv_exact(self, size: int) -> bytes:
        """Receive exact number of bytes."""
        data: bytes = b""
        while len(data) < size:
            chunk: bytes = self.sock.recv(size - len(data))
            if not chunk:
                raise ConnectionError("Connection lost")
            data += chunk
        return data
    
    def recv_line(self) -> str:
        """Receive line (until newline)."""
        buf: bytes = b""
        while b"\n" not in buf:
            chunk: bytes = self.sock.recv(256)
            if not chunk:
                raise ConnectionError("Connection closed")
            buf += chunk
        return buf.partition(b"\n")[0].decode().strip()
    
    def send_command(self, command: str) -> None:
        """Send command to device.
        
        Args:
            command: Command string to send
        """
        if not self.connected:
            raise RuntimeError("Not connected to device")
        self.sock.sendall(command.encode() + b"\n")
    
    def send_bytes(self, data: bytes) -> None:
        """Send raw bytes to device.
        
        Args:
            data: Bytes to send
        """
        if not self.connected:
            raise RuntimeError("Not connected to device")
        self.sock.sendall(data)
    
    def send_file_content(self, file_path: str) -> None:
        """Send file content in chunks.
        
        Args:
            file_path: Path to file to send
        """
        if not self.connected:
            raise RuntimeError("Not connected to device")
        with open(file_path, "rb") as f:
            while chunk := f.read(BUFFER_SIZE):
                self.sock.sendall(chunk)
    
    def save_received_data(self, file_path: str, size: int) -> None:
        """Save received data to file.
        
        Args:
            file_path: Path where to save file
            size: Number of bytes to receive
        """
        data: bytes = self.recv_exact(size)
        with open(file_path, "wb") as f:
            f.write(data)
    
    def is_alive(self, timeout: float = 1.0) -> bool:
        """Check if connection is still alive.
        
        Args:
            timeout: Timeout in seconds for checking
            
        Returns:
            True if connection is active, False otherwise
        """
        if not self.connected or self.sock is None:
            return False
        
        try:
            # Use select to check if socket is readable without blocking
            # A closed socket will be readable and recv will return empty bytes
            ready, _, exceptional = select.select([self.sock], [], [self.sock], timeout)
            
            if exceptional:
                # Socket has an exception
                self.connected = False
                return False
            
            if ready:
                # Socket is readable - try to peek at it without consuming data
                try:
                    data = self.sock.recv(1, socket.MSG_PEEK)
                    if not data:
                        # Empty recv with MSG_PEEK means connection is closed
                        self.connected = False
                        return False
                except:
                    self.connected = False
                    return False
            
            return True
        except:
            self.connected = False
            return False
