import bluetooth

PORT = bluetooth.PORT_ANY
BACKLOG = 1
BUFFER_SIZE = 1024

def run_server():
    server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    server_sock.bind(("", PORT))
    server_sock.listen(BACKLOG)

    port = server_sock.getsockname()[1]

    bluetooth.advertise_service(
        server_sock,
        "BluetoothStringReceiver",
        service_classes=[bluetooth.SERIAL_PORT_CLASS],
        profiles=[bluetooth.SERIAL_PORT_PROFILE],
    )

    print(f"Listening on RFCOMM channel {port}")

    while True:
        print("Waiting for connection...")
        client_sock, client_info = server_sock.accept()
        print(f"Connected to {client_info}")

        try:
            while True:
                data = client_sock.recv(BUFFER_SIZE)
                if not data:
                    print("Client disconnected")
                    break

                print("Received:", data.decode(errors="ignore"))

        except OSError as e:
            print("Connection error:", e)

        finally:
            client_sock.close()
            print("Connection closed\n")

if __name__ == "__main__":
    run_server()
