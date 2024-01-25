# ****************************************************************************
# @file lang_en.py
#
# @author Ángel Fernández Pineda. Madrid. Spain.
# @date 2024-01-25
# @brief Configuration app for ESP32-based open source sim wheels
# @copyright 2024 Ángel Fernández Pineda. Madrid. Spain.
# @license Licensed under the EUPL
# *****************************************************************************

from enum import Enum
from appstrings import install

class EN(Enum):
    _lang = "en"
    _domain = "ESP32SimWheelConfig"
    ALT_BUTTONS = "ALT buttons"
    ALT_MODE = "Alternate mode"
    ANALOG_AXES = "Analog axes"
    AVAILABLE_DEVICES = "Available devices"
    AXIS = "Axis"
    BATTERY = "Battery"
    BITE_POINT = "Bite point"
    BUTTON = "Button"
    BUTTONS_MAP = "Buttons map"
    CHECK_ID = "Check device identity"
    CLUTCH = "Clutch"
    CLUTCH_PADDLES = "Clutch paddles"
    DEFAULTS = "Defaults"
    DONE = "Done!"
    DPAD = "Directional pad"
    ERROR = "Error!"
    FIRMWARE_DEFINED = "Firmware-defined"
    INCLUDE_BTN_MAP = "Include buttons map"
    INVALID_BTN = "Invalid button number (valid numbers are in the range 0-127)"
    LOAD = "Load"
    LOCAL_PROFILE = "Local profile"
    NAV = "Navigation"
    NO_DEVICE = "No device"
    NO_DEVICES_FOUND = "No devices found"
    PROFILE_CHECK_TOOLTIP = "Uncheck to load settings from another sim wheel/button box"
    RECALIBRATE = "Recalibrate"
    REGULAR_BUTTON =  "Regular button"
    RELOAD = "Reload"
    SAVE = "Save"
    SELECT = "Select"
    SOC = "State of charge"
    USER_DEFINED = "User-defined"
    USER_DEFINED_ALT = "User-defined Alt Mode"
    WAIT = "Please, wait..."

install(EN)