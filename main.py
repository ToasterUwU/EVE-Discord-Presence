import os
import datetime
import pypresence
import getpass
import tkinter
import tkinter.ttk as ttkinter
from configparser import ConfigParser

start_time = datetime.datetime.now().timestamp()

conf = ConfigParser()
conf.read("settings.ini")

client_id = "785146044056076328" # Discord Application Client ID. Replace with your own, if you dont use the official build.

presence = pypresence.Presence(client_id)
presence.connect()

tk = tkinter.Tk("EVE Online - Discord Presence")
tk.title("EVE Online - Discord Presence")
try:
    tk.iconbitmap("icon.ico")
except:
    pass
tk.geometry("350x100")

frame = tkinter.Frame()
run_loop = False

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

show_location = tkinter.BooleanVar(frame, value=conf.getboolean("GENERAL", "show_location"))
autostart_presence = tkinter.BooleanVar(frame, value=conf.getboolean("GENERAL", "autostart_presence"))
selected_char = tkinter.StringVar(frame, value=conf.get("GENERAL", "selected_char"))

def get_characters():
    """
    returns a list of all characters
    """
    chars = []
    user = getpass.getuser()
    logs = [x for x in os.scandir(f"C:\\Users\\{user}\\Documents\\EVE\\logs\\Gamelogs")] # Making it a list instead of a custom iterator
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
    user = getpass.getuser()
    logs = [x for x in os.scandir(f"C:\\Users\\{user}\\Documents\\EVE\\logs\\Gamelogs")] # Making it a list instead of a custom iterator
    with open(logs[-1].path, "r") as f: #open latest log
        lines = [x.replace("\n", "") for x in f.readlines()] # Lines without new line char
    return lines

def details(lines=None):
    """
    sets current activity and status
    """
    if lines == None:
        lines = log_lines()

    char = lines[2].split("Listener: ")[1]
    details = {"char": char, "location": "Unknown", "autopilot": False, "docked": True}

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

        elif "Your docking request has been accepted." in line:
            details["docked"] = True
    return details

def loop():
    global run_loop
    if run_loop:
        d = details()

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
            else:
                d["docked"] = "In Space of "

        presence.update(state=d["docked"]+d["location"], details=d['char'], large_image="eve-logo", large_text="EVE Online", small_image=small_img, small_text=small_txt, start=int(start_time))
    else:
        presence.clear()
    tk.after(5000, loop)

def change_loop():
    global run_loop, loop_button
    if run_loop == False:
        run_loop = True
        loop_button["text"] = "Stop Presence"
    else:
        run_loop = False
        loop_button["text"] = "Start Presence"
        presence.clear()

def set_conf():
    conf["GENERAL"] = {
        "show_location": show_location.get(),
        "autostart_presence": autostart_presence.get(),
        "selected_char": selected_char.get(),
    }

    with open('settings.ini', 'w') as config:
        conf.write(config)

loop_button = ttkinter.Button(frame, text="Start Presence", command=change_loop)
loop_button.pack()

location_box = ttkinter.Checkbutton(frame, text="Show Location", variable=show_location, onvalue=True, offvalue=False, command=set_conf)
location_box.pack()

if autostart_presence.get():
    change_loop()

autostart_box = ttkinter.Checkbutton(frame, text="Autostart Presence", variable=autostart_presence, onvalue=True, offvalue=False, command=set_conf)
autostart_box.pack()

chars = get_characters()
if selected_char.get() == "":
    selected_char.set(chars[0])
    set_conf()

character_dropdown = ttkinter.OptionMenu(frame, selected_char, selected_char.get(), *chars, command=set_conf)
character_dropdown.pack()

frame.place(relx=0.5, rely=0.5, anchor="c")

tk.after(0, loop)
tk.mainloop()