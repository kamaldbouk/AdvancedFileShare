# Myriam El Helou

import socket
import threading
import os
import hashlib
import logging

# Server settings
HOST = "0.0.0.0"  # Listen on all interfaces
PORT = 12345
FILE_DIR = "server_files"

# Configure server logging
logging.basicConfig(filename="server.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Ensure the file directory exists
os.makedirs(FILE_DIR, exist_ok=True)

# Function to compute SHA-256 hash of a file
def compute_hash(filepath):
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(4096):
            hasher.update(chunk)
    return hasher.hexdigest()

# Function to handle client requests
def handle_client(client_socket, address):
    logging.info(f"Connected to client: {address}")
    print(f"Connected to {address}")

    while True:
        try:
            request = client_socket.recv(1024).decode()
            if not request:
                break

            logging.info(f"Received request from {address}: {request}")
            command = request.split()

            if command[0] == "UPLOAD":
                filename = command[1]
                filesize = int(command[2])
                receive_file(client_socket, filename, filesize, address)

            elif command[0] == "DOWNLOAD":
                filename = command[1]
                send_file(client_socket, filename, address)

            elif command[0] == "LIST":
                send_file_list(client_socket, address)

        except Exception as e:
            logging.error(f"Error with client {address}: {str(e)}")
            break

    logging.info(f"Connection closed for {address}")
    client_socket.close()


# Function to receive a file from a client
def receive_file(client_socket, filename, filesize, address):
    base, ext = os.path.splitext(filename)
    version = 1
    new_filename = filename
    filepath = os.path.join(FILE_DIR, new_filename)

    while os.path.exists(filepath):
        version += 1
        new_filename = f"{base}_v{version}{ext}"
        filepath = os.path.join(FILE_DIR, new_filename)

    with open(filepath, "wb") as f:
        received_bytes = 0
        while received_bytes < filesize:
            data = client_socket.recv(4096)
            if not data:
                break
            f.write(data)
            received_bytes += len(data)

    server_hash = compute_hash(filepath)
    client_socket.send(f"UPLOAD_COMPLETE {server_hash} {new_filename}".encode())
    logging.info(f"Received file from {address}: {new_filename} ({filesize} bytes)")

# Function to send a file to a client
def send_file(client_socket, filename, address):
    filepath = os.path.join(FILE_DIR, filename)
    
    if not os.path.exists(filepath):
        client_socket.send(b"ERROR: File not found")
        logging.warning(f"File not found for {address}: {filename}")
        return

    filesize = os.path.getsize(filepath)
    client_socket.send(f"FILE {filesize}".encode())

    with open(filepath, "rb") as f:
        while chunk := f.read(4096):
            client_socket.send(chunk)

    logging.info(f"Sent file to {address}: {filename} ({filesize} bytes)")

# Function to send the list of files
def send_file_list(client_socket, address):
    files = os.listdir(FILE_DIR)
    file_list = "\n".join(files) if files else "No files available."
    client_socket.send(file_list.encode())
    logging.info(f"Sent file list to {address}")

# Start the server
def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"Server started on {HOST}:{PORT}")

    while True: # Always listening
        client_socket, address = server.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, address))
        client_thread.start()

start_server()