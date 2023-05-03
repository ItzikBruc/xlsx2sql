# this file is used in case configuration file and xlsx file are given with GUI interface
import os
import pathlib
from tkinter import *
from tkinter import filedialog

from config import Config


def gui_config():
    # Start the main loop
    root.mainloop()

def select_config_file():
    chosen_file_path = filedialog.askopenfilename(
        initialdir=os.getcwd(), title="Configuration",
        filetypes=(("Text files", "*.yaml*"), ("All files", "*.*")))
    if chosen_file_path != '':
        label_file_path.config(text=str(chosen_file_path))
    set_start_button_mode()

def submit():
    Config.yaml_config_path = pathlib.Path(label_file_path.cget("text"))
    # Config.dbms_type_str = dropdown_dbms.get()
    root.destroy()


# noinspection PyUnusedLocal
def on_select_dbms(*args):
    set_start_button_mode()

def set_start_button_mode():
    if label_file_path.cget("text") == 'No file selected':
        button_start.config(state="disabled")
    else:
        button_start.config(state="normal")


# Create the main window
root = Tk()
root.title("Select file")
root.geometry("300x200")
root.protocol("WM_DELETE_WINDOW",  exit)

# Create the button to select file
button_select_config_file = Button(root, text="Select a configuration file", command=lambda: select_config_file(), anchor=CENTER)
button_select_config_file.grid(row=0, column=0, columnspan=2, pady=10, padx=10, ipadx=42, ipady=10)

# Create the file_path_label
label_file_path = Label(root, wraplength=230, text='No file selected', fg="blue", anchor=CENTER, height=3)
label_file_path.grid(row=1, column=0, columnspan=2)

# create select list to choose dbms
'''dropdown_dbms = StringVar(root)
dropdown_dbms.set("Select dbms")
options = ['oracle', 'posgresql']
dropdown_dbms_menu = OptionMenu(root, dropdown_dbms, *options)
dropdown_dbms_menu.grid(row=2, column=0, columnspan=2)
dropdown_dbms.trace("w", on_select_dbms)'''

# create a button to start
button_start = Button(root, text="Start", state=DISABLED, command=lambda: submit())
button_start.grid(row=3, column=0, sticky=W, columnspan=2)

# Create the button to exit
button_exit = Button(root, text="Exit", command=exit)
button_exit.grid(row=3, column=1, sticky=E, columnspan=2)
