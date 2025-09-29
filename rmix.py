import socket
import threading
import re
from time import sleep

MIXER_IP = '192.168.168.40'
MIXER_PORT = 10023

SERVER_IP = '18.223.22.108'
SERVER_PORT = 10000

GUI_IP = '127.0.0.1'

def ipManipulation(data, new_ip):
    m = re.search(rb'(\d{1,3}(?:\.\d{1,3}){3})(\x00+)', data)
    if not m:
        return data

    new_b = new_ip.encode('ascii')
    # OSC: total zeros = 1 (terminator) + padding to 4-byte boundary
    extra = (4 - ((len(new_b) + 1) % 4)) % 4
    zeros = 1 + extra
    replacement = new_b + (b'\x00' * zeros)

    return data[:m.start()] + replacement + data[m.end():]

def server_to_mixer_relay():
    print("Server-to-Mixer relay thread started.")
    while True:
        try:
            # # Receive data from the mixer
            data, addr = server_socket.recvfrom(4096)
            #print(f"Received data: {data} from {addr}")

            # Forward the data to the Mixer
            mixer_socket.sendto(data, (MIXER_IP, MIXER_PORT))
        except Exception as e:
            print(f"Error in Mixer-to-GUI relay: {e}")

def mixer_to_server_relay():
    print("Mixer-to-Server relay thread started.")
    while True:
        try:
            # Receive data from the GUI
            data, addr = mixer_socket.recvfrom(4096)
            #print(f"Received data {data}: from {addr}")

            if (data[:16].decode().startswith("/xinfo") or data[:16].decode().startswith("/status")):
                data = ipManipulation(data, GUI_IP)
                #print(f"Modified data: {data}")

            # Forward the modified data to the mixer
            server_socket.sendto(data, (SERVER_IP, SERVER_PORT))
        except Exception as e:
            print(f"Error in GUI-to-Mixer relay: {e}")


if __name__ == "__main__":

    mixer_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        mixer_socket.bind(('', 0))
        print(f"Client socket bound to port {mixer_socket.getsockname()[1]}")
        server_socket.bind(('', 0))  
        print(f"Server socket bound to port {server_socket.getsockname()[1]}")
    except socket.error as e:
        print(f"Failed to bind client socket: {e}")
        exit()

    # Start relay threads
    server_thread = threading.Thread(target=server_to_mixer_relay, daemon=True)
    mixer_thread = threading.Thread(target=mixer_to_server_relay, daemon=True)
    
    server_thread.start()
    mixer_thread.start()

    # Initial message to server to register this client
    msgToServer = 'Connect - from client 2'.encode('utf-8')
    server_socket.sendto(msgToServer, (SERVER_IP, SERVER_PORT))

    # Keep the main thread alive
    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")
        mixer_socket.close()
        server_socket.close()
        exit()
