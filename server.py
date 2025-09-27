import socket
import threading
from time import sleep


CONNECTIONS = {}

remote_ip = '76.53.3.164'
rmix_ip = '99.24.234.201'
#SERVER_ADDR = ('18.223.22.108', 10000)

#gui_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client2_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#mixer_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

try:
    client_socket.bind(('', 10000))  # Bind to any available port for receiving responses
    print(f"Server socket bound to port {client_socket.getsockname()[1]}")
except socket.error as e:
    print(f"Failed to bind socket: {e}")
    exit()

try:
    client2_socket.bind(('', 0))  # Bind to any available port for receiving responses
    print(f"Server socket bound to port {client2_socket.getsockname()[1]}")
except socket.error as e:
    print(f"Failed to bind socket: {e}")
    exit()
   

def client_to_client_relay():
    print("Server-to-Mixer relay thread started.")
    while True:
        try:
            # Receive data from the server
            data, addr = client_socket.recvfrom(4096)
            print(f"Received data from server {addr}: {data}")

            if addr not in CONNECTIONS.values():
                if addr[0] == remote_ip:
                    CONNECTIONS['REMOTE'] = addr
                    print(f"Remote {addr} stored")
                elif addr[0] == rmix_ip:
                    CONNECTIONS['RMIX'] = addr
                    print(f"Rmix {addr} stored")

            if 'RMIX' in CONNECTIONS:
                client_socket.sendto(data, CONNECTIONS['RMIX'])
                print(f"Forwarded data {data} to mixer at {CONNECTIONS['RMIX']}")
            if 'REMOTE' in CONNECTIONS:
                client_socket.sendto(data, CONNECTIONS['REMOTE'])
                print(f"Forwarded data {data} to remote at {CONNECTIONS['REMOTE']}")
            
            


        except Exception as e:
            print(f"Error in Server-to-Mixer relay: {e}")

# def server_to_gui_relay():
#     print("Server-to-GUI relay thread started.")
#     while True:
#         try:
#             # Receive data from the server
#             data, addr = server_socket.recvfrom(4096)
#             print(f"Received data from server {addr}: {data}")

#             # Forward the data to the GUI
#             if REMOTE_ADDR:
#                 gui_socket.sendto(data, REMOTE_ADDR)
#                 print(f"Forwarded data to GUI at {REMOTE_ADDR}")
#             else:
#                 print("REMOTE_ADDR not set. Cannot forward to GUI.")
#         except Exception as e:
#             print(f"Error in Server-to-GUI relay: {e}")

if __name__ == "__main__":
    # Start relay threads
    client_thread = threading.Thread(target=client_to_client_relay, daemon=True)
    #gui_thread = threading.Thread(target=server_to_gui_relay, daemon=True)
    
    client_thread.start()
    #gui_thread.start()

    # Keep the main thread alive to allow daemon threads to run
    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        print("Shutting down server.")