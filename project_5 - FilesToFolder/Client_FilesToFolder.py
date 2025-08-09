import socket
import tkinter as tk
from tkinter import messagebox
import os
import shutil

# ------------------------------------------------------------------------------------------------------------------------------------
# Client code

def create_client():
    # Creates a socket object for the client
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Create TCP Socket object
    client_socket.connect(("127.0.0.1", 1337)) # Define the IP + Port for the server
    print("Client connected")
    return client_socket


def upload_file(client_socket, file_path):
    # Uploads a file from the client folder to the server folder
    with open(file_path, "rb") as file:
        while True:
            data = file.read(1024) # Reads the first 1024 characters in a file
            # If data is empty
            if not data:
                print("finish sending file")
                break
            print("sending 1024 bytes...")
            # Sends the data to the server
            client_socket.send(data)


def download_file(client_socket, file_path):
    # Download a file from the server folder to the client folder
    with open(file_path, "wb") as file:
        while True:
            data = client_socket.recv(1024) # Receives the first 1024 characters in the file
            # If data is empty
            if not data:
                print("file finished")
                break
            print("received 1024 bytes....")
            # Writing data into the file in the folder of the client
            file.write(data)


client_socket = create_client() # Creating the Client

# End of Client code
# ------------------------------------------------------------------------------------------------------------------------------------


# ------------------------------------------------------------------------------------------------------------------------------------
# GUI code for Client-Server


# Pathes to folders of the Client and the Server
CLIENT_FOLDER = "C://Users//Doron//Documents//client_folder"
SERVER_FOLDER = "C://Users//Doron//Documents//server_folder"

# Creating folders if they don't exist
os.makedirs(CLIENT_FOLDER, exist_ok=True)
os.makedirs(SERVER_FOLDER, exist_ok=True)

# Creating the FileTransferApp class that will contain functions and variables to create a GUI that will be convenient for the Client
class FileTransferApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File upload and download system")

        # --- Client ---
        tk.Label(root, text = "📁 Files in client").grid(row = 0, column = 0)
        self.client_listbox = tk.Listbox(root, width = 130, height = 44)
        self.client_listbox.grid(row = 1, column = 0, padx = 10, pady = 10)

        # --- Server ---
        tk.Label(root, text = "🖥️ Files in Server").grid(row = 0, column = 2)
        self.server_listbox = tk.Listbox(root, width = 130, height = 44)
        self.server_listbox.grid(row = 1, column = 2, padx = 10, pady = 10)

        # --- Buttons ---
        self.upload_button = tk.Button(root, text="⬆️ Upload to server" ,width = 17, height = 4, command = self.upload_file)
        self.upload_button.grid(row = 2, column = 0, pady = 5)

        self.download_button = tk.Button(root, text = "⬇️ Download to client", width = 17, height = 4, command = self.download_file)
        self.download_button.grid(row = 2, column = 2, pady = 5)

        self.refresh_lists()

    def refresh_lists(self):
        # Refreshing the list_box
        # Clear all items from a Listbox widget
        self.client_listbox.delete(0, tk.END)
        self.server_listbox.delete(0, tk.END)

        # Adds the file to the list_box of Client
        for file in os.listdir(CLIENT_FOLDER):
            self.client_listbox.insert(tk.END, file)

        # Adds the file to the list_box of Server
        for file in os.listdir(SERVER_FOLDER):
            self.server_listbox.insert(tk.END, file)


    def upload_file(self):
        selected = self.client_listbox.curselection() # Retrieving the index of the currently selected item within the Listbox
        if not selected:
            messagebox.showwarning("Error", "Select a file to upload from the client")
            return
        filename = self.client_listbox.get(selected[0]) # Gets the file name by index
        src = os.path.join(CLIENT_FOLDER, filename)
        dst = os.path.join(SERVER_FOLDER, filename)
        # Copy a file from a source path (src) to a destination path (dst)
        shutil.copy(src, dst)
        # Refreshing the list_box
        self.refresh_lists()

    def download_file(self):
        selected = self.server_listbox.curselection() # Retrieving the index of the currently selected item within the Listbox
        if not selected:
            messagebox.showwarning("Error", "Select a file to download from the server")
            return
        filename = self.server_listbox.get(selected[0]) # Gets the file name by index
        src = os.path.join(SERVER_FOLDER, filename)
        dst = os.path.join(CLIENT_FOLDER, filename)
        # Copy a file from a source path (src) to a destination path (dst)
        shutil.copy(src, dst)
        # Refreshing the list_box
        self.refresh_lists()


# End of the FileTransferApp class code
# ------------------------------------------------------------------------------------------------------------------------------------

# Running the program
if __name__ == "__main__":
    root = tk.Tk()
    app = FileTransferApp(root)
    root.mainloop()