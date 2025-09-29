import socket
import threading
from time import sleep

CONNECTIONS = {
    'REMOTE': ('', 0),
    'RMIX': ('', 0)
}

active_address = []

def client_to_client_relay():
    print("Server-to-Mixer relay thread started.")
    while True:
        try:
            # Receive data from the server
            data, addr = client_socket.recvfrom(4096)
            if data.startswith(b'/xinfo') and addr not in active_address and addr[0] not in CONNECTIONS['REMOTE'][0]:
                active_address.append(addr)
                CONNECTIONS['REMOTE'] = addr
                print(f"Remote {CONNECTIONS['REMOTE']} stored")
            elif data.startswith(b'Connect') and addr not in active_address and addr[0] not in CONNECTIONS['RMIX'][0]:
                active_address.append(addr)
                CONNECTIONS['RMIX'] = addr
                print(f"Rmix {CONNECTIONS['RMIX']} stored")

            
            for address in active_address:
                if address == addr and addr[0] == CONNECTIONS['REMOTE'][0]:
                    #print(f"Received data from remote {addr}: {data}")
                    try:
                        client_socket.sendto(data, CONNECTIONS['RMIX'])
                    except Exception as e:
                        print(f"Failed to send data to rmix: {e}")
                elif address == addr and addr[0] == CONNECTIONS['RMIX'][0] and not data.startswith(b'Hello'):
                    #print(f"Received data from rmix {addr}: {data}")
                    try:
                        client_socket.sendto(data, CONNECTIONS['REMOTE'])
                    except Exception as e:
                        print(f"Failed to send data to remote: {e}")

        except Exception as e:
            print(f"Error in Server-to-Mixer relay: {e}")


if __name__ == "__main__":

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        client_socket.bind(('', 10000))  # Bind to any available port for receiving responses
        print(f"Server socket bound to port {client_socket.getsockname()[1]}")
    except socket.error as e:
        print(f"Failed to bind socket: {e}")
        exit()

    # Start relay threads
    client_thread = threading.Thread(target=client_to_client_relay, daemon=True)
    
    client_thread.start()

    # Keep the main thread alive to allow daemon threads to run
    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        print("Shutting down server.")
        client_socket.close()
        exit()