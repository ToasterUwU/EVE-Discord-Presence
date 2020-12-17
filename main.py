import os
import time
import datetime
import pypresence
import getpass
import tkinter.messagebox as msgbox
from tkinter import *
from tkinter.ttk import *
from ttkthemes import ThemedTk
from configparser import ConfigParser
import psutil
import webbrowser

conf = ConfigParser()
conf.read("settings.ini")

client_id = "785146044056076328" # Discord Application Client ID. Replace with your own, if you dont use the official build.

settings = ["autostart_presence", "selected_char", "show_location"]
for x in settings:
    if not conf.has_option("GENERAL", x):
        conf["GENERAL"] = {
            "autostart_presence": False,
            "show_location": True,
            "selected_char": "",
        }

        with open('settings.ini', 'w') as config:
            conf.write(config)

        break

def get_characters():
    """
    returns a list of all characters
    """
    chars = []
    logs = [x for x in os.scandir(log_location)] # Making it a list instead of a custom iterator

    for log in logs:
        with open(log.path, "r") as f:
            try:
                lines = [x.replace("\n", "") for x in f.readlines()]
                chars.append(lines[2].split("Listener: ")[1])
            except:
                pass
    chars = list(dict.fromkeys(chars))
    return chars

def log_lines():
    """
    returns list of lines in latest log
    """
    logs = [x for x in os.scandir(log_location)] # Making it a list instead of a custom iterator
    logs.reverse()
    char = selected_char.get()

    for log in logs:
        with open(log.path, "r") as f: #open latest log
            lines = [x.replace("\n", "") for x in f.readlines()] # Lines without new line char
            try:
                if lines[2].split("Listener: ")[1] == char:
                    return lines
            except IndexError:
                pass

def details(lines=None):
    """
    sets current activity and status
    """
    if lines == None:
        lines = log_lines()

    char = lines[2].split("Listener: ")[1]
    start_time = int((datetime.datetime.strptime(lines[3].split("Session Started: ")[1], "%Y.%m.%d %H:%M:%S") + datetime.timedelta(hours=(-time.timezone/3600))).timestamp()) #get time in own timezone from log file (i know, super complicated)
    details = {"char": char, "start_time": start_time, "location": "Unknown", "autopilot": False, "docked": True, "station": False} #set default values

    for line in lines:
        if "Undocking from" in line:
            details["location"] = line.split(" to ")[1].replace(" solar system.", "")
            details["docked"] = False

        elif "Jumping from" in line:
            details["location"] = line.split(" to ")[1]

        elif "Autopilot engaged" in line:
            details["autopilot"] = True

        elif "Autopilot disabled" in line:
            details["autopilot"] = False

        elif "Requested to dock at" in line:
            details["station"] = line.split("Requested to dock at ")[1].replace(" station", "")

        elif "Your docking request has been accepted." in line:
            details["docked"] = True
    return details

def loop():
    global run_loop
    if run_loop:
        d = details()

        # here comes the logic part
        if d["autopilot"] == False:
            if d["docked"]:
                small_img = "docked"
                small_txt = "Docked"
            else:
                small_img = "manual"
                small_txt = "Manual flight"
        else:
            small_img = "auto"
            small_txt = "Autopilot"

        if not show_location.get():
            d["location"] = ""

            if d["docked"]:
                d["docked"] = "Docked"
            else:
                d["docked"] = "In Space"
        else:
            if d["docked"]:
                d["docked"] = "Docked in "
                if d["station"]:
                    d["location"] = d["station"]

            else:
                d["docked"] = "In Space of "

        presence.update(state=d["docked"]+d["location"], details=d['char'], large_image="eve-logo", large_text="EVE Discord Presence --> Get it on Github: bit.ly/2JZQHkK", small_image=small_img, small_text=small_txt, start=int(d["start_time"]))
        status_message.config(text=f"{d['char']}\n{d['docked']+d['location']}\n{small_txt}")
    tk.after(5000, loop) #repeat after 5 seconds

def change_loop():
    global run_loop, loop_button
    if run_loop == False:
        try:
            presence.connect()
        except pypresence.exceptions.InvalidPipe:
            msgbox.showerror("An Error occoured", "Discord doesnt seem to run. Please start Discord and then try again.")
            exit()

        if "eve_crashmon.exe" not in (p.name() for p in psutil.process_iter()):
            return msgbox.showwarning("EVE Online is not running", "To use this program, you need to have EVE Online started.")
        run_loop = True
        loop_button["text"] = "Stop Presence"
    else:
        run_loop = False
        loop_button["text"] = "Start Presence"
        presence.clear()
        presence.close()
        status_message.config(text="Presence offline")

def set_conf(*args):
    conf["GENERAL"] = {
        "show_location": show_location.get(),
        "autostart_presence": autostart_presence.get(),
        "selected_char": selected_char.get(),
    }

    with open('settings.ini', 'w') as config:
        conf.write(config)

presence = pypresence.Presence(client_id)

tk = ThemedTk("EVE Online - Discord Presence", theme="arc")
tk.title("EVE Online - Discord Presence")
try:
    tk.iconbitmap("icon.ico")
except:
    pass
tk.geometry("350x150")

frame = Frame(tk)

run_loop = False
user = getpass.getuser()
log_location = f"C:\\Users\\{user}\\Documents\\EVE\\logs\\Gamelogs"
show_location = BooleanVar(frame, value=conf.getboolean("GENERAL", "show_location"))
autostart_presence = BooleanVar(frame, value=conf.getboolean("GENERAL", "autostart_presence"))
selected_char = StringVar(frame, value=conf.get("GENERAL", "selected_char"))

loop_button = Button(frame, text="Start Presence", command=change_loop)
loop_button.grid(column=1, row=1)

location_box = Checkbutton(frame, text="Show Location", variable=show_location, onvalue=True, offvalue=False, command=set_conf)
location_box.grid(column=0, row=0)

if autostart_presence.get():
    change_loop()
autostart_box = Checkbutton(frame, text="Autostart Presence", variable=autostart_presence, onvalue=True, offvalue=False, command=set_conf)
autostart_box.grid(column=0, row=1)

chars = get_characters()
if selected_char.get() == "":
    selected_char.set(chars[0])
    set_conf()

character_dropdown = OptionMenu(frame, selected_char, selected_char.get(), *chars, command=set_conf)
character_dropdown.grid(column=1, row=0)

status_message = Message(frame, width=300)
status_message.grid(column=0, columnspan=2, row=2)

credit_button = Button(frame, text="Github Page", command=lambda: webbrowser.open("https://github.com/ToasterUwU/EVE-Discord-Presence"))
credit_button.grid(column=0, columnspan=2, row=3)

frame.place(relx=0.5, rely=0.5, anchor="c")

tk.after(0, loop)
tk.mainloop()