import os
import time
import pypresence
import getpass
import tkinter
import tkinter.ttk as ttkinter
import threading

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

run_th = False
show_location = tkinter.BooleanVar(frame, value=True)

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

def loop_thread():
    global run_th
    while run_th:
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

        presence.update(state=d["docked"]+d["location"], details=d['char'], large_image="eve-logo", large_text="EVE Online", small_image=small_img, small_text=small_txt)
        time.sleep(5)

def change_th():
    global th, run_th, th_button
    if run_th == False:
        th = threading.Thread(target=loop_thread, daemon=True)
        run_th = True
        th.start()
        th_button["text"] = "Stop Presence"
    else:
        run_th = False
        th_button["text"] = "Start Presence"
        presence.clear()

th_button = ttkinter.Button(frame, text="Start Presence", command=change_th)
th_button.pack()

location_box = ttkinter.Checkbutton(frame, text="Show Location", variable=show_location, onvalue=True, offvalue=False)
location_box.pack()

frame.place(relx=0.5, rely=0.5, anchor="c")

tk.mainloop()