import os
from typing import List
if not __name__ == "__main__":
    from Bluetooth.base_client import BluetoothClientBase

BUFFER_SIZE: int = 1024

class TrainingBluetoothClient(BluetoothClientBase):
    """Manages training configuration transfer and execution via Bluetooth."""
    
    def __init__(self, mac: str, channel: int = 1, timeout: int = 10) -> None:
        """Initialize training Bluetooth client.
        
        Args:
            mac: MAC address of device
            channel: RFCOMM channel (default: 1)
            timeout: Socket timeout in seconds (default: 10)
        """
        super().__init__(mac, channel, timeout)
    
    def send_file(self, training_id: str, path: str) -> str:
        """Send file to device.
        
        Args:
            training_id: Training identifier
            path: Path to file to send
            
        Returns:
            Server response message
        """
        if not self.connected:
            raise RuntimeError("Not connected to device")
        
        filename: str = os.path.basename(path)
        filesize: int = os.path.getsize(path)

        self.send_command(f"CMD SEND {training_id} {filename} {filesize}")
        resp: str = self.recv_line()
        if resp != "READY":
            raise RuntimeError(f"Server not ready: {resp}")

        self.send_file_content(path)
        return self.recv_line()
    
    def request_file(self, filename: str, save_path: str) -> None:
        """Request file from device.
        
        Args:
            filename: Name of file to request
            save_path: Path where to save received file
        """
        if not self.connected:
            raise RuntimeError("Not connected to device")
        
        self.send_command(f"CMD REQ {filename}")

        header: str = self.recv_line()
        parts: List[str] = header.split()
        if parts[:3] != ["CMD", "SEND", "OUT"]:
            raise RuntimeError(f"Invalid server response: {header}")

        filesize: int = int(parts[4])
        self.send_bytes(b"READY\n")

        self.save_received_data(save_path, filesize)
    
    def start_training(self, training_id: str) -> str:
        """Start training on device.
        
        Args:
            training_id: Training identifier
            
        Returns:
            Server response message
        """
        if not self.connected:
            raise RuntimeError("Not connected to device")
        
        self.send_command(f"CMD START {training_id}")
        return self.recv_line()
    
    def stop_training(self) -> str:
        """Stop training on device.
        
        Returns:
            Server response message
        """
        if not self.connected:
            raise RuntimeError("Not connected to device")
        
        self.send_command("CMD STOP")
        return self.recv_line()
    
    def ping(self) -> bool:
        """Send heartbeat ping to server.
        
        Returns:
            True if server responds with PONG, False otherwise
        """
        if not self.connected:
            return False
        
        try:
            self.send_command("CMD PING")
            resp: str = self.recv_line()
            return resp == "PONG"
        except:
            self.connected = False
            return False

def print_help() -> None:
    """Print available commands."""
    print("\n=== Available Commands ===")
    print("  send <training_id> <file_path>")
    print("      Send a merged training YAML file to the device")
    print("      Example: send training1 /path/to/MergedTrainingFile.yaml")
    print()
    print("  request <filename> <save_path>")
    print("      Request a file from the device")
    print("      Example: request output.csv /local/path/output.csv")
    print()
    print("  start <training_id>")
    print("      Start training on the device")
    print("      Example: start training1")
    print()
    print("  help")
    print("      Show this help message")
    print()
    print("  quit")
    print("      Disconnect and exit")
    print("=======================\n")

def main() -> None:
    """Interactive CLI for training Bluetooth client."""
    mac: str = input("MAC: ").strip()
    channel: int = int(input("Channel: "))

    client: TrainingBluetoothClient = TrainingBluetoothClient(mac, channel)
    
    try:
        client.connect()
        print(f"Connected to {mac}")
        print_help()
        
        while True:
            cmd: List[str] = input("> ").strip().split()
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
                
                elif cmd[0] == "stop":
                    client.send_command("CMD STOP")
                    print("Server:", client.recv_line())

                elif cmd[0] == "help":
                    print_help()

                elif cmd[0] == "quit":
                    break
                
                else:
                    print("Unknown command. Type 'help' for available commands.")
            
            except Exception as e:
                print(f"Error: {str(e)}")
    
    finally:
        client.disconnect()

if __name__ == "__main__":
    from base_client import BluetoothClientBase
    main()
