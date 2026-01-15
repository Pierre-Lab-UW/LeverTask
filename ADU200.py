import hid
from typing import Optional, Union
import time
from zmq import device

class ADU200:
    _instance: Optional["ADU200"] = None

    def __init__(self, vendor_id: int = 0x0A07, product_id: int = 0x00C8) -> None:
        if ADU200._instance is not None:
            raise Exception("Use ADU200.get_instance() instead of creating a new object directly.")
        
        self.vendor_id: int = vendor_id
        self.product_id: int = product_id
        self.device: Optional[hid.device] = None
        self.connect()
        ADU200._instance = self

        

    @classmethod
    def get_instance(cls) -> "ADU200":
        try:
            if cls._instance is None:
                cls._instance = ADU200()
            return cls._instance
        except Exception as e:
            print(f"Error getting ADU200 instance: {e}")
            return None

    def connect(self) -> None:
        try:
            self.device = hid.device()
            self.device.open(self.vendor_id, self.product_id)
            print(f'Connected to ADU{self.product_id:02X}')

            # Clear any existing data in the buffer
            timer = time.time()
            while time.time() - timer < 200:  # 200 ms timeout
                data = self.read() # Read data
                if not data:
                    break # Buffer is empty

        except IOError as e:
            print(f'Error opening device: {e}')
            self.device = None

    def disconnect(self) -> None:
        if self.device:
            self.device.close()
            print("Device disconnected.")
            self.device = None

    def write(self, msg_str: str) -> Optional[int]:
        if not self.device:
            print("Device not connected.")
            return None

        #print(f'Writing command: {msg_str}')
        byte_str: str = chr(0x01) + msg_str + chr(0) * max(7 - len(msg_str), 0)

        try:
            return self.device.write(byte_str.encode())
        except IOError as e:
            print(f'Error writing command: {e}')
            return None
    
    def set_relay(self, relay_num, set_open=True):
        if set_open:
            self.write('RK'+str(relay_num))
        else:
            self.write('SK'+str(relay_num))

    def read(self, timeout: int = 200) -> Optional[str]:
        if not self.device:
            print("Device not connected.")
            return None

        try:
            data = self.device.read(8, timeout)
        except IOError as e:
            print(f'Error reading response: {e}')
            return None

        if not data:
            return None

        byte_str: str = ''.join(chr(n) for n in data[1:])
        result_str: str = byte_str.split('\x00', 1)[0]

        return result_str if result_str else None

    def get_port_status(self, port: int) -> Optional[int]:
        # print(f"Getting port status for port {port}")
        self.write('RPA'+str(port))
        data = self.read()
        # print(f"Received data: {data}")
        if data is not None:
            try:
                return int(data)
            except ValueError:
                print(f"Invalid data received: {data}")
        return None

    def read_port_register(self):
        self.write('RPA')
        data = self.read()
        if data is not None:
            try:
                return int(data)
            except ValueError:
                print(f"Invalid data received: {data}")
        return None

    @staticmethod
    def list_devices(vendor_id: int = 0x0A07) -> None:
        print('Connected ADU devices:')
        for d in hid.enumerate(vendor_id):
            print(f'    Product ID: {d["product_id"]}')
        print()


if __name__ == "__main__":
    import time

    adu = ADU200.get_instance()

    try:
        for i in range(5):
            print(f"Cycle {i+1}: Turning relay 0 ON")
            adu.set_relay(0, set_open=False)
            adu.set_relay(1, set_open=False)
            time.sleep(2)

            print(f"Cycle {i+1}: Turning relay 0 OFF")
            adu.set_relay(0, set_open=True)
            adu.set_relay(1, set_open=True)
            time.sleep(2)
        
        while True:
            port_status = adu.read_port_register()
            print(f"Port status: {port_status}")
            time.sleep(1)
            
    except Exception as e:
        print(f"An error occurred: {e}")
    
    
