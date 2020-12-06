import os
import time
import pypresence
import getpass

client_id = "785146044056076328" # Discord Application Client ID. Replace with your own, if you dont use the official build.

presence = pypresence.Presence(client_id)
presence.connect()

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
    details = {"char": char, "location": "Unknown", "autopilot": False, "docked": "Docked in "}

    for line in lines:
        if "(None)" in line:
            if "Undocking from" in line:
                details["location"] = line.split(" to ")[1].replace(" solar system.", "")
                details["docked"] = "In Space of "

            elif "Jumping from" in line:
                details["location"] = line.split(" to ")[1]

        elif "Autopilot engaged" in line:
            details["autopilot"] = True

        elif "Autopilot disabled" in line:
            details["autopilot"] = False

        elif "Your docking request has been accepted." in line:
            details["docked"] = "Docked in "
    return details

while True:
    d = details()

    if d["autopilot"] == False:
        small_img = "manual"
        small_txt = "Manual flight"
    else:
        small_img = "auto"
        small_txt = "Autopilot"

    presence.update(state=d["docked"]+d["location"], details=d['char'], large_image="eve-logo", large_text="EVE Online", small_image=small_img, small_text=small_txt)
    time.sleep(5)