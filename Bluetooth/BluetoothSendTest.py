import bluetooth
import struct
import zlib
import os

CHUNK_SIZE = 1024

print("Scanning for Bluetooth devices...")
devices = bluetooth.discover_devices(duration=8, lookup_names=True)

if not devices:
    print("No Bluetooth devices found")
    exit(1)

for i, (addr, name) in enumerate(devices):
    print(f"[{i}] {name} ({addr})")

choice = int(input("Select device number: "))
target_addr, target_name = devices[choice]

print(f"Connecting to {target_name} ({target_addr})")

# RFCOMM channel — usually 1 for SPP
PORT = 1

sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
sock.connect((target_addr, PORT))

filepath = input("File to send: ")
filename = os.path.basename(filepath)
file_size = os.path.getsize(filepath)

crc = 0

# ---- Send filename ----
sock.send(struct.pack("!I", len(filename)))
sock.send(filename.encode())

# ---- Send file size ----
sock.send(struct.pack("!Q", file_size))

# ---- Send file ----
with open(filepath, "rb") as f:
    while True:
        data = f.read(CHUNK_SIZE)
        if not data:
            break
        sock.send(data)
        crc = zlib.crc32(data, crc)

# ---- Send CRC ----
sock.send(struct.pack("!I", crc))

sock.close()
print("✅ File sent successfully")
