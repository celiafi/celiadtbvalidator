from tkinter import *
from tkinter import filedialog
import celia_dtb_validator
import os
import sys
import pathlib
from modules import config_getter
from modules.path_checker import PathChecker
import tkinter.messagebox
from shutil import which
import webbrowser


def change_value(entry):
    new_path = filedialog.askdirectory()
    entry.config(state="normal")
    entry.delete(0, END)
    entry.insert(0, new_path)
    entry.config(state="readonly")


def run_validator(path, o_path, r_path):
    gui.withdraw()
    if pathlib.Path(path).exists() and pathlib.Path(r_path).exists() and pathlib.Path(o_path).exists():
        print("Running validation for book " + path)
        celia_dtb_validator.CeliaDTBValidator.run_validation(path, o_path, r_path)
        input("Press enter to continue...")
        os.system('cls')
    else:
        print("Path error!")
        tkinter.messagebox.showerror("PATH ERROR!", "PATH ERROR!")
        os.system('cls')
    gui.deiconify()


def open_manua():
    manualfile = pathlib.Path.joinpath(pathlib.Path(__file__).parent, "manual.html")
    # print(str(manualfile))
    if manualfile.exists():
        webbrowser.open(str(manualfile))


# MAIN...
if __name__ == "__main__":

    #if which("sox") is None:
    #    input("sox not found from PATH! Please install sox before running validator.")
    #    sys.exit()

    if config_getter.ConfigGetter.get_configs("audio_validation") == "1":
        if not PathChecker.check_audio_ext_paths():
            input("FFmpeg not found. Please install FFmpeg and/or define FFmpeg path in config.txt")
            sys.exit()

    if config_getter.ConfigGetter.get_configs("daisy_validation") == "1":
        if not PathChecker.check_daisy_ext_paths():
            input("Pipeline 1 or java not found. Please install Pipeline 1 and java and/or define Pipeline 1 and java paths in config.txt")
            sys.exit()

    
    # if which("ffmpeg") is None:
    #     input("ffmpeg not found from PATH! Please install ffmpeg before running validator.")
    #     sys.exit()

    gui = Tk()
    gui.title("Celia DTB Validator GUI")
    iconfile = pathlib.Path.joinpath(pathlib.Path(__file__).parent, "img/logo.ico")
    gui.iconbitmap(str(iconfile))
    Label(gui, text="Input path", font=("Times", 14)).grid(row=0, sticky=W, padx=10)
    Label(gui, text="Output path", font=("Times", 14)).grid(row=2, sticky=W, padx=10)
    Label(gui, text="Report path", font=("Times", 14)).grid(row=4, sticky=W, padx=10)

    # Input path
    e1 = Entry(gui, width=80, font=("Times", 14))
    e1.delete(0, END)
    e1.insert(0, "C:/Temp")
    e1.config(state="readonly")

    # Output path
    e2 = Entry(gui, width=80, font=("Times", 14))
    e2.delete(0, END)
    e2.insert(0, "C:/Temp")
    e2.config(state="readonly")

    # Report path
    e3 = Entry(gui, width=80, font=("Times", 14))
    e3.delete(0, END)
    e3.insert(0, "C:/Temp")
    e3.config(state="readonly")

    e1.grid(row=1, column=0, padx=(10, 0))
    e2.grid(row=3, column=0, padx=(10, 0))
    e3.grid(row=5, column=0, padx=(10, 0), pady=10)

    # BUTTONS
    b1 = Button(gui, text="Change input path", font=("Times", 14), command=lambda: change_value(e1))
    b1.grid(row=1, column=2)

    b2 = Button(gui, text="Change output path", font=("Times", 14), command=lambda: change_value(e2))
    b2.grid(row=3, column=2)

    b3 = Button(gui, text="Change report path", font=("Times", 14), command=lambda: change_value(e3))
    b3.grid(row=5, column=2)

    b4 = Button(gui, text="Open config file", font=("Times", 14),
                command=lambda: config_getter.ConfigGetter.open_config_file())
    b4.grid(row=6, column=0, padx=10, sticky=W)

    b5 = Button(gui, height=2, width=20, text="START VALIDATION", font=("Times", 18), bg="green",
                command=lambda: run_validator(e1.get(), e2.get(), e3.get()))
    b5.grid(row=6, column=2, padx=10, columnspan=4, pady=5)

    # MENU
    menubar = Menu(gui)
    menubar = Menu(menubar)
    helpmenu = Menu(menubar, tearoff=0)
    helpmenu.add_command(label="Change input path", command=lambda: change_value(e1))
    helpmenu.add_command(label="Change output path", command=lambda: change_value(e2))
    helpmenu.add_command(label="Change report path", command=lambda: change_value(e3))
    helpmenu.add_separator()
    helpmenu.add_command(label="Run validation", command=lambda: run_validator(e1.get(), e2.get(), e3.get()))
    helpmenu.add_separator()
    helpmenu.add_command(label="Open config file", command=lambda: config_getter.ConfigGetter.open_config_file())
    helpmenu.add_command(label="Open manual", command=lambda: open_manua())
    helpmenu.add_separator()
    helpmenu.add_command(label="Exit", command=gui.quit)
    menubar.add_cascade(label="Menu", menu=helpmenu)
    gui.configure(menu=menubar)

    gui.mainloop()
