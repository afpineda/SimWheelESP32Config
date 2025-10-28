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
import shutil
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
    license_file = Path("./LICENSE")
    app_name = "ESP32SimWheel"
    output_folder = Path(f"./dist/{app_name}")
    build_folder = Path(f"./build/{app_name}")

    cmd = [
        "nicegui-pack",
        f"{main_file}",  # your main file with ui.run()
        "--name",
        app_name,  # name of your app
        "--windowed",  # prevent console from appearing, only use with ui.run(native=True, ...)
        "--icon",
        f"{icons_file}",
    ]
    print("Launching freezer: ")
    for s in cmd:
        print(s, end=" ")
    print("")
    shutil.rmtree(output_folder, ignore_errors=True)
    shutil.rmtree(build_folder, ignore_errors=True)
    subprocess.call(cmd)
    shutil.copy(license_file, f"{output_folder}{os.sep}LICENSE.txt")

else:
    print("ERROR: this script must run in the project root...")
    exit(-1)

# Reminder: to make a zip in linux
#   cd dist
#   zip -r -q linux ESP32SimWheel/
