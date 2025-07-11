import hid
from typing import Optional, Union

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
        if cls._instance is None:
            cls._instance = ADU200()
        return cls._instance

    def connect(self) -> None:
        try:
            self.device = hid.device()
            self.device.open(self.vendor_id, self.product_id)
            print(f'Connected to ADU{self.product_id:02X}')
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
        self.write('RPA'+str(port))
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
