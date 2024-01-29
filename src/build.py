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

    cmd = [
        "pyinstaller",
        "src/ESP32SimWheelConfig/__main__.py",  # your main file with ui.run()
        "--name",
        "ESP32SimWheel",  # name of your app
        #'--onefile',
        "--windowed",  # prevent console appearing, only use with ui.run(native=True, ...)
        "--add-data",
        f"{Path(nicegui.__file__).parent}{os.pathsep}nicegui",
        "--add-data",
        f"./LICENSE{os.pathsep}.",
        "-i",
        "resources/MainIcons.ico",
        "--hidden-import",
        "src/ESP32SimWheelConfig/esp32simwheel.py",
    ]
    print("Launching freezer: ")
    for s in cmd:
        print(s, end=" ")
    print("")
    subprocess.call(cmd)

else:
    print("ERROR: this script must run in the project root...")
    exit(-1)
