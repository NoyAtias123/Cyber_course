import tkinter as tk
from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageTk
import os
import time
import requests

#-----------------------------------------------------------------------------------------------
# Anti Virus with api key code:

virus_total_api_scan_url = "https://www.virustotal.com/vtapi/v2/file/scan"
virus_total_get_report_url = "https://www.virustotal.com/vtapi/v2/file/report"
virus_total_api_key = os.getenv("Virus_Total_Api_Key")

FILE_WAITING_IN_QUEUE_CODE = -2

def scan_file(file_path):
    # Scanning a file and checking the number of positives (viruses in the file)
    scan_id = upload_file(file_path)
    while True:
        report = get_report(scan_id)
        if "response_code" in report and report["response_code"] == FILE_WAITING_IN_QUEUE_CODE:
            time.sleep(10)
            continue
        elif "positives" in report:
            return report["positives"]


def upload_file(file_path):
    # Creates a connection to the virustotal api website and uploads the file there (not including a scan operation)
    params = {'apikey': virus_total_api_key}
    files = {'file': (file_path, open(file_path, 'rb'))} 
    response = requests.post(virus_total_api_scan_url, files=files, params=params)
    response = response.json()
    return response["scan_id"]


def get_report(scan_id):
    # Performs the scan operation on the site and returns the result
    params = {'apikey': virus_total_api_key, 'resource': scan_id}
    response = requests.get(virus_total_get_report_url, params=params)
    if not response:
        raise Exception("Unexpected error in response")
    
    if response.status_code == 204:
        response = {"response_code":FILE_WAITING_IN_QUEUE_CODE} 
        return response
    else:
        return response.json()


def get_all_files_from_folder(folder_path):
    # Finds all file paths in the given folder and returns them in a list
    files_list = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            files_list.append(os.path.join(root, file))
    return files_list

# End of the Anti Virus with api key code
#-----------------------------------------------------------------------------------------------


#-----------------------------------------------------------------------------------------------
# Graphical User Interface code for the Anti Virus code

def adding_image(image_path, frame):
    # Creates a background image for the frame
    original_image = Image.open(image_path)
    resized_image = original_image.resize((1600, 900))
    img = ImageTk.PhotoImage(resized_image)
    background = Label(frame, image = img)
    background.image = img
    background.pack()


def buttons(buttons_commands, frame):
    # Creates buttons that will appear on the screen
    for key, value in buttons_commands.items():
        key = Button(frame, text = key, width = value[2], height = value[3], font = ('Courier', value[4]), fg = "white",
                        activebackground = value[5], bg = "navy", command = value[6])
        key.place(x = value[0], y = value[1])        

def show_frame(frame_to_show):
    # Replaces the frame with another frame
    frame_to_show.tkraise() 

def help_button():
    # Switches from default_frame to help_frame
    show_frame(help_frame)

def back_to_default_frame():
    # Switches from frame to default_frame
    show_frame(default_frame)

def open_files_in_computer():
    # Switches from default_frame to file_frame
    show_frame(file_frame)  

def open_folders_in_computer():
    # Switches from default_frame to folder_frame
    show_frame(folder_frame)

def choose_file():
    # Opens the files on the computer and lets the user insert the file they want
    global file_path_var
    file_path = filedialog.askopenfilename(title = "Select a file to scan")
    if file_path:
        file_path_var.set(file_path)

def choose_folder():
    # Opens the files on the computer and lets the user insert the folder they want
    global folder_path_var
    folder_path = filedialog.askdirectory(title = "Select a folder to scan")
    if folder_path:
        folder_path_var.set(folder_path)

def result_message(file_path, positives):
    # Returns a message depending on the number of positives
    if positives == 0:
        return f"✅The file: {file_path} is completely clean - NO viruses!😀✅\n"
    elif positives > 0:
        return f"⛔The file: {file_path} contains {positives} viruses❗❗❗⛔\n"
    else:
        return f"⚠️Error scanning {file_path}: {positives}⚠️\n"
    
def result_of_scanning_file():
    # Creates a text box for result_frame with the result of scanning the file
    file = file_path_var.get().strip()
    show_frame(loading_frame)
    gui.update()  # Update the text box to the frame         
    positives = scan_file(file)            
    result_box.delete("1.0", tk.END) # Deletes the information in a text box each time
    result_box.insert(tk.END, result_message(file, positives))
    show_frame(result_frame)


def result_of_scanning_folder():
    # Creates a text box for result_frame with the result of scanning all files in folder
    folder = folder_path_var.get().strip()
    show_frame(loading_frame)
    gui.update() # Update the text box to the frame
    result_box.delete("1.0", tk.END) # Deletes the information in a text box each time
    for file_path in get_all_files_from_folder(folder):
        positives = scan_file(file_path)
        result_box.insert(tk.END, result_message(file_path, positives))
        gui.update()
    show_frame(result_frame)


def animate_gif_background(frame, gif_path, delay = 230):
    # Creating a label to use as a background GIF image
    frames = []
    idx = 0
    while True:
        try:
            # Saving the different frames of the GIF in a list
            frames.append(PhotoImage(file = gif_path, format=f"gif -index {idx}"))
            idx += 1
        except TclError:
            break
    
    # Creating a label in the desired frame
    bg = Label(frame)               
    bg.place(relwidth = 1, relheight = 1)  
    bg.lower()                         

    def play(i = 0):
        # Causes the first frame to appear using the label
        bg.config(image=frames[i])    
        # Switches to the next frame after a certain set time
        frame.after(delay, play, (i+1) % len(frames))

    # Prevents Python from collecting the images (otherwise the GIF will disappear after a few seconds)
    frame._gif_frames = frames
    play()


# Creating GUI 
gui = Tk(baseName = "Anti_Virus_App", className = 'Anti_Virus_app')
gui.geometry("1600x900")

file_path_var = tk.StringVar()
folder_path_var = tk.StringVar()

# (x, y, width, height, font, activebackground, bg, commend)
buttons_commands = {'SCAN FILE': (240, 500, 40, 8, 16, "pink", open_files_in_computer),
                    'SCAN PATH': (870, 500, 40, 8, 16, "pink", open_folders_in_computer), 'HELP':(1300, 740, 25, 4, 12, "purple", help_button)}
exit = {'EXIT': (50, 740, 25, 4, 12, "red", gui.destroy)}
back_default = {'<-- BACK': (50, 70, 25, 3, 12, "yellow", back_to_default_frame)}
select_file = {'Select file': (670, 470, 25, 3, 12, "pink", choose_file)}
select_folder = {'Select folder': (670, 470, 25, 3, 12, "pink", choose_folder)}
submit_file = {'SUBMIT': (670, 550, 25, 3, 12, "green", result_of_scanning_file)}
submit_folder = {'SUBMIT': (670, 550, 25, 3, 12, "green", result_of_scanning_folder)}


# Creating default_frame - home screen: appears every time you open the interface (default)
default_frame = Frame(gui, width = 1600, height = 900)
default_frame.place(x = 0, y = 0, relwidth = 1, relheight = 1)
animate_gif_background(default_frame, "D://NOY//אקדמיית המתכנתים//default_frame.gif")
buttons(buttons_commands, default_frame)
buttons(exit, default_frame)


# Creating file_frame - frame where the user inserts the file they want to scan
file_frame = tk.Frame(gui, width = 1600, height = 900)
adding_image("D://NOY//אקדמיית המתכנתים//empty_frame.png", file_frame)
file_frame.place(x = 0, y = 0, relwidth = 1, relheight = 1)
# Creates a label that tells the user what to do
file_path_label = Label(file_frame, text = 'Enter file path', font = ('calibre',32, 'bold'))
file_path_label.place(relx = 0.5, rely = 0.42, anchor = tk.CENTER) 
# Creates an entry where the user can enter the desired path
entry_file_path = Entry(file_frame, textvariable = file_path_var, width = 60, font = ('calibre',20,'normal'))
entry_file_path.place(relx = 0.5, rely = 0.5, anchor = tk.CENTER) 
buttons(back_default, file_frame)
buttons(submit_file, file_frame)
buttons(exit, file_frame)
buttons(select_file, file_frame)


# Creating folder_frame - frame where the user inserts the folder they want to scan
folder_frame = Frame(gui, width = 1600, height = 900)
adding_image("D://NOY//אקדמיית המתכנתים//empty_frame.png", folder_frame)
folder_frame.place(x = 0, y = 0, relwidth = 1, relheight = 1)
# Creates a label that tells the user what to do
folder_path_label = Label(folder_frame, text = 'Enter folder path', font = ('calibre',32, 'bold'))
folder_path_label.place(relx = 0.5, rely = 0.42, anchor = tk.CENTER) 
# Creates an entry where the user can enter the desired path
entry_folder_path = Entry(folder_frame, textvariable = folder_path_var, width = 60, font = ('calibre',20,'normal'))
entry_folder_path.place(relx = 0.5, rely = 0.5, anchor = tk.CENTER) 
buttons(back_default, folder_frame)
buttons(submit_folder, folder_frame)
buttons(exit, folder_frame)
buttons(select_folder, folder_frame)


# Creating help_frame - explains the buttons on the home screen (default_frame)
help_frame = Frame(gui, width = 1600, height = 900)
adding_image("D://NOY//אקדמיית המתכנתים//help_frame.png", help_frame)
help_frame.place(x = 0, y = 0, relwidth = 1, relheight = 1)
buttons(back_default, help_frame)
buttons(exit, help_frame)


# Creating loading_frame - displayed while the program is running and scanning the file
loading_frame = Frame(gui, width = 1600, height = 900)
adding_image("D://NOY//אקדמיית המתכנתים//loading_frame.png", loading_frame)
loading_frame.place(x = 0, y = 0, relwidth = 1, relheight = 1)
buttons(exit, loading_frame)


# Creating result_frame - displays the results of scanning the file or folder
result_frame = Frame(gui, width = 1600, height = 900)
adding_image("D://NOY//אקדמיית המתכנתים//empty_frame.png", result_frame)
result_frame.place(x = 0, y = 0, relwidth = 1, relheight = 1)
# Creating a text box that will contain the scan result(s)
result_box = Text(result_frame, bg = "black",fg = "white",font = ('calibre',20,'normal'), width = 120, height = 10)
result_box.place(relx = 0.5, rely = 0.5, anchor = tk.CENTER)
buttons(exit, result_frame)

show_frame(default_frame)

#End of Graphical User Interface code for the Anti Virus code
#-----------------------------------------------------------------------------------------------

def main():
    gui.mainloop() # Running the interface


if __name__ == "__main__":
    main()