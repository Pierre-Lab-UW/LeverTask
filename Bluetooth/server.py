import os
import socket
import subprocess
from typing import Optional, Tuple, List
from base_server import BluetoothServerBase

class TrainingBluetoothServer(BluetoothServerBase):
    """Manages training session execution via Bluetooth RFCOMM server."""
    
    def __init__(self, mac: str, channel: int = 4, rx_dir: str = "/tmp/bluetooth_rx", output_dir: str = "OutputData/") -> None:
        """Initialize training Bluetooth server.
        
        Args:
            mac: MAC address to bind to
            channel: RFCOMM channel (default: 4)
            rx_dir: Directory for received files (default: /tmp/bluetooth_rx)
            output_dir: Directory for output files (default: /data/outputs)
        """
        super().__init__(mac, channel)
        self.rx_dir: str = rx_dir
        self.output_dir: str = output_dir
        self.active_process: Optional[subprocess.Popen] = None
    
    def _handle_send(self, parts: List[str]) -> None:
        """Handle CMD SEND - receive file from client."""
        _, _, training_id, filename, filesize = parts
        filesize_int: int = int(filesize)

        train_dir: str = os.path.join(self.rx_dir, training_id)
        os.makedirs(train_dir, exist_ok=True)
        filepath: str = os.path.join(train_dir, os.path.basename(filename))

        self.send_bytes(b"READY\n")
        self.save_received_file(filepath, filesize_int)

        self.send_bytes(b"OK\n")
        print("Received:", filepath)
    
    def _handle_request(self, parts: List[str]) -> None:
        """Handle CMD REQ - send output file to client."""
        _, _, filename = parts
        path: str = os.path.join(self.output_dir, os.path.basename(filename))
        
        if not os.path.isfile(path):
            avalible_files: str = "\n".join(os.listdir(self.output_dir))
            #send all files names in output dir to client for user convenience
            self.send_message(f"ERR-Invalid file request. Available files:\n{avalible_files}")
            return

        size: int = os.path.getsize(path)
        self.send_message(f"CMD SEND OUT {filename} {size}")

        if self.recv_line() != "READY":
            return

        self.send_file_content(path)
        print("Sent:", filename)
    
    def _handle_start(self, parts: List[str]) -> None:
        """Handle CMD START - start training on device."""
        if self.is_running():
            self.send_message("ERR: Training already running")
            return

        training_id: str = parts[2]
        path: str = os.path.join(self.rx_dir, training_id)

        # Check if required files exist
        if (not os.path.isdir(path) or 
            not os.path.isfile(os.path.join(path, "GlobalParameters.yaml")) or 
            not os.path.isfile(os.path.join(path, "RatioTraining.yaml"))):
            self.send_message("ERR: Missing required files!")
            return

        # Start training process
        self.active_process = subprocess.Popen([
            "python3", "main.py",
            os.path.join(path, "GlobalParameters.yaml"),
            os.path.join(path, "RatioTraining.yaml")
        ])

        self.send_bytes(b"OK\n")
    
    def _handle_stop(self) -> None:
        """Handle CMD STOP - stop training on device."""
        if self.is_running():
            self.active_process.terminate()
            self.active_process.wait()
            self.active_process = None
            self.send_message("STOPPED TRAINING!")
        else:
            self.send_message("ERR: No training running")
    
    def _handle_client(self, client: socket.socket, addr: Tuple[str, int]) -> None:
        """Handle client connection."""
        self.sock = client
        print("Connected:", addr)
        try:
            while True:
                line: str = self.recv_line()
                parts: List[str] = line.split()

                if parts[:2] == ["CMD", "SEND"]:
                    self._handle_send(parts)

                elif parts[:2] == ["CMD", "REQ"]:
                    self._handle_request(parts)
                
                elif parts[:2] == ["CMD", "STOP"]:
                    self._handle_stop()

                elif parts[:2] == ["CMD", "START"]:
                    self._handle_start(parts)
                else:
                    self.send_bytes(b"ERR - Invalid command\n")

        except (ConnectionError, OSError) as e:
            print("Disconnected:", e)

        finally:
            client.close()
    
    def start(self) -> None:
        """Start the training Bluetooth server with output directory setup."""
        os.makedirs(self.rx_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        super().start()
    
    def is_running(self) -> bool:
        """Check if training process is running."""
        return self.active_process is not None and self.active_process.poll() is None

def main() -> None:
    """Run training Bluetooth server."""
    server: TrainingBluetoothServer = TrainingBluetoothServer("B8:27:EB:7E:6F:9D", channel=4)
    server.start()

if __name__ == "__main__":
    main()
