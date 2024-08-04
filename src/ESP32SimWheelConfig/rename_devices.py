# ****************************************************************************
# @file rename_devices.py
#
# @author Ángel Fernández Pineda. Madrid. Spain.
# @date 2024-08-04
# @brief Access specific keys in the windows registry related to device names
# @copyright 2024 Ángel Fernández Pineda. Madrid. Spain.
# @license Licensed under the EUPL
# *****************************************************************************

"""
Access specific keys in the windows registry related to device names

Functions:

    get_display_name_from_registry()
    set_display_name_in_registry()

"""

###############################################################################

import winreg
from sys import platform

__all__ = [
    "get_display_name_from_registry",
    "set_display_name_in_registry",
]

###############################################################################

__KEY_ROOT = r"System\\CurrentControlSet\\Control\\MediaProperties\\PrivateProperties\\Joystick\\OEM\\VID_"
__VALUE_OEM_NAME = "OEMName"

###############################################################################


def _compute_key(vid: int, pid: int) -> str:
    vid_hex = f"{vid:#0{6}x}"[2:].upper()
    pid_hex = f"{pid:#0{6}x}"[2:].upper()
    return __KEY_ROOT + vid_hex + "&PID_" + pid_hex


def get_display_name_from_registry(vid: int, pid: int) -> str | None:
    """Get the device display name from the Windows registry"""
    if platform != "win32":
        return None
    key = _compute_key(vid, pid)
    try:
        key_handle = winreg.OpenKeyEx(winreg.HKEY_CURRENT_USER, key)
        try:
            return winreg.QueryValueEx(key_handle, __VALUE_OEM_NAME)[0]
        finally:
            key_handle.Close()
    except FileNotFoundError:
        return None


def set_display_name_in_registry(
    vid: int, pid: int, new_name: str | None
) -> str | None:
    """Set the device display name in the Windows registry"""
    if platform == "win32":
        key = _compute_key(vid, pid)
        key_handle = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, key)
        try:
            if (new_name == None) or (new_name == ""):
                try:
                    winreg.DeleteValue(key_handle, __VALUE_OEM_NAME)
                except FileNotFoundError:
                    pass
            else:
                winreg.SetValueEx(key_handle, __VALUE_OEM_NAME, 0, winreg.REG_SZ, new_name)
        finally:
            key_handle.Close()
