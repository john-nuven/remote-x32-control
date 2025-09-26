import socket
import threading
import re

GUI_IP = "127.0.0.1"

MIXER_IP = '192.168.168.40'
MIXER_PORT = 10023

mixer_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

try:
    mixer_socket.bind(('', 10023))  # Bind to any available port for receiving mixer responses
    print(f"Mixer socket bound to port {mixer_socket.getsockname()[1]}")
except socket.error as e:
    print(f"Failed to bind mixer socket: {e}")
    exit()

# try:
#     server_socket.bind(('', 0))  # Bind to any available port for receiving server responses
#     print(f"Server socket bound to port {server_socket.getsockname()[1]}")
# except socket.error as e:
#     print(f"Failed to bind server socket: {e}")
#     exit()

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

def mixer_to_server_relay():
    print("Mixer-to-Server relay thread started.")
    while True:
        try:
            # Receive data from the GUI
            data, addr = mixer_socket.recvfrom(4096)
            print(f"Received data from GUI {addr}: {data}")

            if (data[:16].decode().startswith("/xinfo") or data[:16].decode().startswith("/status")):
                data = ipManipulation(data, GUI_IP)
                print(f"Modified data: {data}")

            # Forward the modified data to the mixer
            server_socket.sendto(data, ('18.223.22.108', 10000))
        except Exception as e:
            print(f"Error in GUI-to-Mixer relay: {e}")


if __name__ == "__main__":
    # Start relay threads
    mixer_thread = threading.Thread(target=mixer_to_server_relay, daemon=True)
    
    mixer_thread.start()
    
    # Keep the main thread alive
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Shutting down...")
        mixer_socket.close()
        server_socket.close()
        exit()
