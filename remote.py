import socket
import threading
import time

GUI_IP = '127.0.0.1'
GUI_PORT = 10023

def gui_to_server_relay():
    print("GUI-to-Server relay thread started.")
    while True:
        try:
            # Receive data from the GUI
            data, addr = gui_socket.recvfrom(4096)
            print(f"Received data from GUI {addr}: {data}")

            # Forward the data to the server
            server_socket.sendto(data, ('18.223.22.108', 10000))
            print(f"Forwarded data {data} to server at {'18.223.22.108'}:{10000}")
        except Exception as e:
            print(f"Error in GUI-to-Server relay: {e}")

def server_to_gui_relay():
    print("Server-to-GUI relay thread started.")
    while True:
        try:
            # Receive data from the server
            data, addr = server_socket.recvfrom(4096)
            print(f"Received data from server {addr}: {data}")

            # Forward the data to the GUI
            gui_socket.sendto(data, (GUI_IP, GUI_PORT))
            print(f"Forwarded data to GUI at {GUI_IP}:{GUI_PORT}")
        except Exception as e:
            print(f"Error in Server-to-GUI relay: {e}")

if __name__ == "__main__":
    gui_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        gui_socket.bind((GUI_IP, GUI_PORT))
        print(f"Server listening on {GUI_IP}:{GUI_PORT}")
    except socket.error as e:
        print(f"Failed to bind socket: {e}")
        exit()

    try:
        server_socket.bind(('', 0))  # Bind to any available port for receiving responses
        print(f"Server socket bound to port {server_socket.getsockname()[1]}")
    except socket.error as e:
        print(f"Failed to bind server socket: {e}")
        exit()

    # Start relay threads
    gui_thread = threading.Thread(target=gui_to_server_relay, daemon=True)
    server_thread = threading.Thread(target=server_to_gui_relay, daemon=True)
    
    gui_thread.start()
    server_thread.start()

    # Keep the main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")
        gui_socket.close()
        server_socket.close()
        exit()  
