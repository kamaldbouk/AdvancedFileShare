# Kamal Dbouk

import socket
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import hashlib
import logging

# Server details
SERVER_IP = "127.0.0.1"
SERVER_PORT = 12345
BUFFER_SIZE = 4096

# Configure client logging
logging.basicConfig(filename="client.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Function to compute SHA-256 hash
def compute_hash(filepath):
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(4096):
            hasher.update(chunk)
    return hasher.hexdigest()

# Function to upload a file
def upload_file():
    filename = filedialog.askopenfilename()
    if not filename:
        return

    try:
        file_size = os.path.getsize(filename)
        logging.info(f"Uploading file: {filename} ({file_size} bytes)")
        client_socket.send(f"UPLOAD {os.path.basename(filename)} {file_size}".encode())

        with open(filename, "rb") as f:
            sent_bytes = 0
            while chunk := f.read(BUFFER_SIZE):
                client_socket.send(chunk)
                sent_bytes += len(chunk)
                progress["value"] = (sent_bytes / file_size) * 100
                root.update_idletasks()

        response = client_socket.recv(1024).decode()
        if response.startswith("UPLOAD_COMPLETE"):
            parts = response.split()
            server_hash = parts[1]
            saved_filename = parts[2]
            local_hash = compute_hash(filename)

        if local_hash == server_hash:
            logging.info(f"File uploaded successfully: {saved_filename}")
            if saved_filename != os.path.basename(filename):
                messagebox.showinfo("File Uploaded", f"File renamed and uploaded as {saved_filename}")
            else:
                messagebox.showinfo("Success", "File uploaded successfully!")
        else:
            logging.error(f"Hash mismatch for uploaded file: {filename}")
            messagebox.showerror("Error", "File upload failed due to hash mismatch")
    except Exception as e:
        logging.error(f"Error during upload: {str(e)}")
        messagebox.showerror("Error", f"Upload failed: {str(e)}")


# Function to download a file
def download_file():
    filename = file_entry.get()
    if not filename:
        messagebox.showerror("Error", "Enter a filename to download.")
        return

    try:
        client_socket.send(f"DOWNLOAD {filename}".encode())
        response = client_socket.recv(1024).decode()

        if response.startswith("FILE"):
            file_size = int(response.split()[1])
            logging.info(f"Downloading file: {filename} ({file_size} bytes)")
            save_path = filedialog.asksaveasfilename(initialfile=filename)
            if not save_path:
                return

            with open(save_path, "wb") as f:
                received_bytes = 0
                while received_bytes < file_size:
                    data = client_socket.recv(BUFFER_SIZE)
                    f.write(data)
                    received_bytes += len(data)
                    progress["value"] = (received_bytes / file_size) * 100
                    root.update_idletasks()

            logging.info(f"File downloaded successfully: {filename}")
            messagebox.showinfo("Success", "File downloaded successfully!")
        else:
            logging.warning(f"Failed to download file: {filename}. Server response: {response}")
            messagebox.showerror("Error", response)
    except Exception as e:
        logging.error(f"Error during download: {str(e)}")
        messagebox.showerror("Error", f"Download failed: {str(e)}")


# Function to list available files
def list_files():
    try:
        client_socket.send("LIST".encode())
        response = client_socket.recv(4096).decode()
        file_list.delete(0, tk.END)
        for file in response.split("\n"):
            file_list.insert(tk.END, file)
        logging.info("Fetched file list from server.")
    except Exception as e:
        logging.error(f"Error fetching file list: {str(e)}")
        messagebox.showerror("Error", "Failed to fetch file list.")

# GUI setup
root = tk.Tk()
root.title("File Sharing System")

tk.Button(root, text="Upload File", command=upload_file).pack(pady=5)

file_entry = tk.Entry(root)
file_entry.pack(pady=5)

tk.Button(root, text="Download File", command=download_file).pack(pady=5)

tk.Button(root, text="Refresh Files", command=list_files).pack(pady=5)
file_list = tk.Listbox(root, width=50, height=10)
file_list.pack(pady=5)

progress = ttk.Progressbar(root, length=300, mode="determinate")
progress.pack(pady=5)

# Connect to the server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_IP, SERVER_PORT))

root.mainloop()

client_socket.close()