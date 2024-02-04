# ****************************************************************************
# @file build.py
#
# @author Ángel Fernández Pineda. Madrid. Spain.
# @date 2024-01-21
# @brief Configuration app for ESP32-based open source sim wheels
# @copyright 2024 Ángel Fernández Pineda. Madrid. Spain.
# @license Licensed under the EUPL
# *****************************************************************************

# -------------------------- IMPORTANT NOTE --------------------------------
# Your antivirus may get in the way
# Add an exception rule
# -------------------------- IMPORTANT NOTE --------------------------------

import os
import subprocess
from pathlib import Path
import nicegui
from os.path import exists

if exists(".gitignore") and exists(".gitattributes"):
    print("--------------------------------------------------------------")
    print("ESP32SimWheelConfig: freezing for distribution                ")
    print("--------------------------------------------------------------")

    main_file = Path("src/ESP32SimWheelConfig/__main__.py")
    icons_file = Path("resources/MainIcons.ico")
    sim_wheel_api_file = Path("src/ESP32SimWheelConfig/esp32simwheel.py")
    license_file = Path("./LICENSE")

    cmd = [
        "pyinstaller",
        f"{main_file}",  # your main file with ui.run()
        "--name",
        "ESP32SimWheel",  # name of your app
        #'--onefile',
        "--windowed",  # prevent console appearing, only use with ui.run(native=True, ...)
        "--add-data",
        f"{Path(nicegui.__file__).parent}{os.pathsep}nicegui",
        "--add-data",
        f"{license_file}{os.pathsep}.",
        "-i",
        f"{icons_file}",
        "--hidden-import",
        f"{sim_wheel_api_file}",
    ]
    print("Launching freezer: ")
    for s in cmd:
        print(s, end=" ")
    print("")
    subprocess.call(cmd)

else:
    print("ERROR: this script must run in the project root...")
    exit(-1)

# Reminder: to make a zip in linux
#   cd dist
#   zip -r -q linux ESP32SimWheel/