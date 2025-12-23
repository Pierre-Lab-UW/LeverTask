import serial
import os
import time

BUFFER_SIZE = 1024

def send_file(ser, training_id, filepath):
    if not os.path.isfile(filepath):
        print("File does not exist:", filepath)
        return

    filename = os.path.basename(filepath)
    filesize = os.path.getsize(filepath)

    # Send header
    cmd = f"CMD SEND {training_id} {filename} {filesize}\n"
    ser.write(cmd.encode())
    ser.flush()

    print(f"Sending file {filename} ({filesize} bytes)...")
    with open(filepath, "rb") as f:
        while True:
            chunk = f.read(BUFFER_SIZE)
            if not chunk:
                break
            ser.write(chunk)
            ser.flush()

    # Wait for acknowledgment
    resp = ser.readline().decode().strip()
    print("PI response:", resp)


def request_file(ser, filename, save_path):
    ser.write(f"CMD REQ {filename}\n".encode())
    ser.flush()

    header = ser.readline().decode().strip()
    parts = header.split()
    if parts[:2] != ["CMD", "SEND"]:
        print("Failed to request file:", header)
        return

    filesize = int(parts[4])
    print(f"Receiving file {filename} ({filesize} bytes)...")

    received = 0
    with open(save_path, "wb") as f:
        while received < filesize:
            chunk = ser.read(min(BUFFER_SIZE, filesize - received))
            if not chunk:
                raise ConnectionError("Connection lost")
            f.write(chunk)
            received += len(chunk)

    print(f"File saved to {save_path}")


def main():
    serial_port = input("Enter RFCOMM serial port (e.g., /dev/rfcomm0): ")
    try:
        ser = serial.Serial(serial_port, baudrate=115200, timeout=1)
        time.sleep(2)
    except Exception as e:
        print("Failed to open serial port:", e)
        return

    print("Connected. Enter commands:")
    print("  send <training_id> <file_path>")
    print("  request <filename> <save_path>")
    print("  quit")

    try:
        while True:
            cmd = input("> ").strip()
            if not cmd:
                continue

            parts = cmd.split()
            if parts[0].lower() == "send" and len(parts) == 3:
                send_file(ser, parts[1], parts[2])

            elif parts[0].lower() == "request" and len(parts) == 3:
                request_file(ser, parts[1], parts[2])

            elif parts[0].lower() == "start" and len(parts) == 2:
                cmd = f"CMD START {parts[1]}\n"
                ser.write(cmd.encode())

            elif parts[0].lower() == "quit":
                print("Exiting...")
                break

            else:
                print("Unknown command or wrong number of arguments.")

    finally:
        ser.close()
        print("Disconnected.")


if __name__ == "__main__":
    main()
