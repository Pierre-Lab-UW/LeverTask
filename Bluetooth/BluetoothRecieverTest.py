import bluetooth

# Create RFCOMM server socket
server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

# Bind to any available port
server_sock.bind(("", bluetooth.PORT_ANY))
server_sock.listen(1)

port = server_sock.getsockname()[1]

print(f"Listening for Bluetooth connections on RFCOMM channel {port}")

# Advertise service so devices can discover it
bluetooth.advertise_service(
    server_sock,
    "BluetoothStringReceiver",
    service_classes=[bluetooth.SERIAL_PORT_CLASS],
    profiles=[bluetooth.SERIAL_PORT_PROFILE],
)

# Wait for a connection
client_sock, client_info = server_sock.accept()
print(f"Accepted connection from {client_info}")

try:
    while True:
        data = client_sock.recv(1024)
        if not data:
            break

        # Decode and print received string
        print("Received:", data.decode(errors="ignore"))

except KeyboardInterrupt:
    print("\nClosing connection")

finally:
    client_sock.close()
    server_sock.close()
