import socket
from abc import ABC, abstractmethod

BUFFER_SIZE = 1024

class BluetoothClientBase(ABC):
    """Base class for Bluetooth RFCOMM clients. Handles socket communication logic."""
    
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
    
    def _recv_exact(self, size):
        """Receive exact number of bytes."""
        data = b""
        while len(data) < size:
            chunk = self.sock.recv(size - len(data))
            if not chunk:
                raise ConnectionError("Connection lost")
            data += chunk
        return data
    
    def _recv_line(self):
        """Receive line (until newline)."""
        buf = b""
        while b"\n" not in buf:
            chunk = self.sock.recv(256)
            if not chunk:
                raise ConnectionError("Connection closed")
            buf += chunk
        return buf.partition(b"\n")[0].decode().strip()
    
    def _send_command(self, command):
        """Send command to device.
        
        Args:
            command: Command string to send
        """
        if not self.connected:
            raise RuntimeError("Not connected to device")
        self.sock.sendall(command.encode() + b"\n")
