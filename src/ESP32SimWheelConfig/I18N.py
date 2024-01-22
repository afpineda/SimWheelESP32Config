# ****************************************************************************
#  @author Ángel Fernández Pineda. Madrid. Spain.
#  @date 2024-01-21
#  @brief Configuration app for ESP32-based open source sim wheels
#  @copyright Creative Commons Attribution 4.0 International (CC BY 4.0)
# *****************************************************************************

import os
import subprocess
from pathlib import Path
from os.path import exists

if exists(".gitignore") and exists(".gitattributes"):
    print("--------------------------------------------------------------")
    print("ESP32SimWheelConfig: Compile internationalization files       ")
    print("--------------------------------------------------------------")

    locales = ['en','es']

    for locale in locales:
        cmd = [
            "c:\\PublicApps\\gettext\\bin\\msgfmt.exe",
            "-o",
            f"src\\ESP32SimWheelConfig\\locale\\{locale}\\LC_MESSAGES\\ESP32SimWheel.mo",
            f"src\\ESP32SimWheelConfig\\locale\\{locale}\\LC_MESSAGES\\ESP32SimWheel.po"
        ]
        subprocess.call(cmd)
    print("Done!")

else:
    print("ERROR: this script must run in the project root...")
    exit(-1)
