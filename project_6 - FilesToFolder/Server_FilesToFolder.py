import socket

def create_server():
    # Creates a socket object for the server
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Create TCP Socket object
    server_socket.bind(("127.0.0.1", 1337)) # Define the IP + Port for the server
    server_socket.listen(5) # Define maximum amount ot connections waiting to be accepted
    print(f"Listening for new connections")
    return server_socket

def accept_client(server_socket):
    # Accepts an incoming connection request from a client
    client_socket, client_address = server_socket.accept()
    print(f"Connection established with {client_address}")
    return client_socket


def download_file(client_socket, file_path):
    # Download a file from the client folder to the server folder
    with open(file_path, "wb") as file:
        while True:
            data = client_socket.recv(1024) # Receives the first 1024 characters in the file
            # If data is empty
            if not data:
                print("file finished")
                break
            print("received 1024 bytes....")
            # Writing data into the file in the folder of the server
            file.write(data)

def upload_file(client_socket, file_path):
    # Uploads a file from the server folder to the client folder
    with open(file_path, "rb") as file:
        while True:
            data = file.read(1024) # Reads the first 1024 characters in a file
            # If data is empty
            if not data:
                print("finish sending file")
                break
            print("sending 1024 bytes...")
            # Sends the data to the client
            client_socket.send(data)


server_sock = create_server() # Creating the Server
client_sock = accept_client(server_sock) # Accepting requests from clients
