# ****************************************************************************
# @file esp32simwheel.py
#
# @author Ángel Fernández Pineda. Madrid. Spain.
# @date 2024-01-21
# @brief Configuration app for ESP32-based open source sim wheels
# @copyright 2024 Ángel Fernández Pineda. Madrid. Spain.
# @license Licensed under the EUPL
# *****************************************************************************

"""
Retrieve instances of connected ESP32 open sim wheel devices

Classes:

    SimWheel

Enumerations:

    ClutchPaddlesWorkingMode

Functions:

    enumerate()

Exceptions:

    AnotherAppInterferesError
"""
###############################################################################

import hid
import struct
from enum import IntEnum

###############################################################################

_CONTROLLER_TYPE = 5

_RID_CAPABILITIES = 2
_RID_CONFIG = 3
_RID_BUTTONS_MAP = 4

_REPORT_SIZE_CAPABILITIES = 17
_REPORT_SIZE_CONFIG = 6
_REPORT_SIZE_BUTTONS_MAP = 4

_CAP_CLUTCH_BUTTON = 0  # has digital clutch paddles (switches)
_CAP_CLUTCH_ANALOG = 1  # has analog clutch paddles (potentiometers)
_CAP_ALT = 2  # has "ALT" buttons
_CAP_DPAD = 3  # has a directional pad
_CAP_BATTERY = 4  # battery-operated
_CAP_BATTERY_CALIBRATION_AVAILABLE = 5  # has battery calibration data

###############################################################################


class AnotherAppInterferesError(Exception):
    """Raised when another application is interfering in the reading of buttons maps."""

    pass


###############################################################################


class ClutchPaddlesWorkingMode(IntEnum):
    """Working modes of clutch paddles.

    CLUTCH : F1-style clutch
    AXIS   : Independent analog axes
    ALT    : Alternate mode
    BUTTON : Regular buttons
    """

    CLUTCH = 0
    AXIS = 1
    ALT = 2
    BUTTON = 3


###############################################################################


class SimWheel:
    """A class to represent an ESP32 open-source sim wheel or button box."""

    def __init__(self, path: str = ""):
        """Create a representation of an ESP32 open-source sim wheel or button box."""
        self._hid = hid.device()
        self.__path = path
        self.__is_open = False
        self.__is_sim_wheel = None

    def __del__(self):
        self.close()

    def _open(self):
        if (
            (self.__is_sim_wheel != False)
            and (not self.__is_open)
            and (self.__path != "")
        ):
            try:
                self._hid.open_path(self.__path)
                self.__is_open = True
                if self.__is_sim_wheel == None:
                    self.__is_sim_wheel = self._check_is_sim_wheel()
            except:
                self.__is_open = False

    def _check_is_sim_wheel(self) -> bool:
        """Determine if this device is an ESP32 open-source sim wheel or not."""
        try:
            # Get "capabilities" report (ID #2)
            raw = bytes(
                self._hid.get_feature_report(
                    _RID_CAPABILITIES, _REPORT_SIZE_CAPABILITIES
                )
            )
            # Get magic number, data version and flags
            data = struct.unpack("HHHH", raw[1:9])
            checkFailed = data[0] != 48977  # Expected magic number
            checkFailed = checkFailed or (data[1] != 1)  # Check major version
            if checkFailed:
                return False
            self.__dataMajorVersion = data[1]
            self.__dataMinorVersion = data[2]
            self._capabilityFlags = data[3]
            # At data version 1.1, get device ID
            if len(raw) >= 17:
                data = struct.unpack("Q", raw[9:17])
                self.deviceID = data[0]
            # Confirm the "configuration" report is available
            self._hid.get_feature_report(_RID_CONFIG, _REPORT_SIZE_CONFIG)
            # At data version 1.1, confirm the "buttons map" report is available
            if (self.__dataMajorVersion == 1) and (self.__dataMinorVersion >= 1):
                self._hid.get_feature_report(_RID_BUTTONS_MAP, _REPORT_SIZE_BUTTONS_MAP)
            return True
        except:
            return False

    def _get_config_report(self):
        """Read a device configuration feature report (id #3)."""
        data = bytes(self._hid.get_feature_report(_RID_CONFIG, _REPORT_SIZE_CONFIG))
        if self.__dataMinorVersion >= 1:
            return struct.unpack("BBBBB", data[1:6])
        else:
            return struct.unpack("BBBB", data[1:5])

    def _send_config_report(self, data: bytes):
        """Writes a device configuration feature report (id #3)."""
        aux = bytearray(_REPORT_SIZE_CONFIG)
        aux[0] = _RID_CONFIG
        aux[1] = data[0]
        aux[2] = data[1]
        aux[3] = data[2]
        aux[4] = data[3]
        if self.__dataMajorVersion >= 1:
            aux[5] = data[4]
            self._hid.send_feature_report(aux)
        else:
            self._hid.send_feature_report(aux[0:5])

    def _get_buttons_map_report(self):
        """Read a buttons map feature report (id #4)."""
        if self.__dataMinorVersion >= 1:
            data = bytes(
                self._hid.get_feature_report(_RID_BUTTONS_MAP, _REPORT_SIZE_BUTTONS_MAP)
            )
            return struct.unpack("BBB", data[1:4])
        else:
            return ()

    def _send_buttons_map_report(self, data: bytes):
        """Writes a buttons map feature ."""
        aux = bytearray(_REPORT_SIZE_BUTTONS_MAP)
        aux[0] = _RID_BUTTONS_MAP
        aux[1] = data[0]
        aux[2] = data[1]
        aux[3] = data[2]
        self._hid.send_feature_report(aux)

    def _is_ready(self):
        """Returns True if the device is connected and ready for user configuration."""
        self._open()
        return (self.__is_sim_wheel == True) and (self.__is_open)

    def close(self):
        """Close HID connection."""
        try:
            self._hid.close()
        except:
            pass
        self.__is_open = False

    @property
    def is_alive(self) -> bool:
        """Returns True if this device is still connected"""
        self._open()
        try:
            self._get_config_report()
        except:
            self.close()
        return self.__is_open

    @property
    def is_sim_wheel(self) -> bool:
        """Returns True if this device is an ESP32 open-source sim wheel or button box."""
        self._open()
        return bool(self.__is_sim_wheel)

    @property
    def has_buttons_map(self) -> bool:
        """Returns True if this device supports user-defined button maps."""
        if self._is_ready():
            return self.__dataMinorVersion >= 1
        else:
            return False

    @property
    def has_clutch(self) -> bool:
        """Returns True if this device has clutch paddles (any kind)."""
        if self._is_ready():
            return bool(
                ((1 << _CAP_CLUTCH_ANALOG) | (1 << _CAP_CLUTCH_BUTTON))
                & self._capabilityFlags
            )
        else:
            return False

    @property
    def has_analog_clutch_paddles(self) -> bool:
        """Returns True if this device has analog clutch paddles."""
        if self._is_ready():
            return bool((1 << _CAP_CLUTCH_ANALOG) & self._capabilityFlags)
        else:
            return False

    @property
    def has_dpad(self) -> bool:
        """Returns True if this device has navigational controls."""
        if self._is_ready():
            return bool((1 << _CAP_DPAD) & self._capabilityFlags)
        else:
            return False

    @property
    def has_alt_buttons(self) -> bool:
        """Returns True if this device has ALT buttons."""
        if self._is_ready():
            return bool((1 << _CAP_ALT) & self._capabilityFlags)
        else:
            return False

    @property
    def has_battery(self) -> bool:
        """Returns True if this device is powered by batteries."""
        if self._is_ready():
            return bool((1 << _CAP_BATTERY) & self._capabilityFlags)
        else:
            return False

    @property
    def battery_calibration_available(self) -> bool:
        """Returns True if this device is able to auto-calibrate battery's state of charge."""
        if self._is_ready():
            return bool(
                (1 << _CAP_BATTERY_CALIBRATION_AVAILABLE) & self._capabilityFlags
            )
        else:
            return False

    @property
    def batter_soc(self) -> int:
        """Returns a percentage (0..100) of current battery charge"""
        if self._is_ready():
            try:
                report = self._get_config_report()
                return report[3]
            except:
                self.close()
        else:
            return 100

    @property
    def dataMajorVersion(self) -> int:
        """Major version of the data interchange specification supported by this device."""
        if self._is_ready():
            return self.__dataMajorVersion
        else:
            return 0

    @property
    def dataMinorVersion(self) -> int:
        """Minor version of the data interchange specification supported by this device."""
        if self._is_ready():
            return self.__dataMinorVersion
        else:
            return 0

    @property
    def clutch_working_mode(self) -> ClutchPaddlesWorkingMode:
        """Returns the current working mode of clutch paddles.

        This value has no meaning if there are no clutch paddles.
        Check has_clutch_paddles first.
        """
        if self._is_ready():
            try:
                report = self._get_config_report()
                return ClutchPaddlesWorkingMode(report[0])
            except:
                self.close()
                return ClutchPaddlesWorkingMode.CLUTCH

    @clutch_working_mode.setter
    def clutch_working_mode(self, mode: ClutchPaddlesWorkingMode):
        """Set the working mode of clutch paddles.

        No effect if there are no clutch paddles.
        """
        if self._is_ready():
            try:
                self._send_config_report((int(mode), 0xFF, 0xFF, 0xFF, 0xFF))
            except:
                self.close()

    @property
    def alt_buttons_working_mode(self) -> bool:
        """Returns the working mode of ALT buttons.

        True for alternate mode, False for regular buttons mode.
        This value has no meaning if there are no ALT buttons.
        Check has_alt_buttons first.
        """
        if self._is_ready():
            try:
                report = self._get_config_report()
                return bool(report[1])
            except:
                self.close()

    @alt_buttons_working_mode.setter
    def alt_buttons_working_mode(self, mode: bool):
        """Set the working mode of ALT buttons.

        No effect if there are no ALT buttons.
        """
        if self._is_ready():
            try:
                self._send_config_report((0xFF, int(mode), 0xFF, 0xFF, 0xFF))
            except:
                self.close()

    @property
    def bite_point(self) -> int:
        """Returns the current clutch's bite point.

        A value in the range from 0 to 254, inclusive.
        Non-meaningful if there are no clutch paddles.
        """
        if self._is_ready():
            try:
                report = self._get_config_report()
                return report[2]
            except:
                self.close()

    @bite_point.setter
    def bite_point(self, value: int):
        """Sets the clutch's bite point.

        No effect if there are no clutch paddles.
        """
        if (value < 0) or (value > 254):
            raise ValueError("Bite point not in the range 0..254")
        if self._is_ready():
            try:
                self._send_config_report((0xFF, 0xFF, value, 0xFF, 0xFF))
            except:
                self.close()

    @property
    def dpad_working_mode(self) -> bool:
        """Returns the working mode of navigational controls.

        True for navigation, False for regular buttons mode.
        This value has no meaning if there are no navigational controls.
        Check has_dpad first.
        """
        if self._is_ready():
            try:
                report = self._get_config_report()
                return bool(report[4])
            except:
                self.close()
        else:
            return False

    @dpad_working_mode.setter
    def dpad_working_mode(self, mode: bool):
        """Set the working mode of navigational controls.

        No effect if there are no navigational controls.
        """
        if self._is_ready():
            try:
                self._send_config_report((0xFF, 0xFF, 0xFF, 0xFF, int(mode)))
            except:
                self.close()

    @property
    def path(self) -> str:
        """OS path to this device."""
        return self.__path

    @path.setter
    def path(self, path: str):
        if self.__path != path:
            self.close()
            self.__path = path
            self.__is_sim_wheel = None

    @property
    def manufacturer(self) -> str:
        """Name of the manufacturer of this device."""
        self._open()
        if self.__is_open:
            return self._hid.get_manufacturer_string()
        else:
            return ""

    @property
    def product_name(self) -> str:
        """Product name of this device."""
        self._open()
        if self.__is_open:
            return self._hid.get_product_string()
        else:
            return ""

    def recalibrate_analog_axes(self):
        """Force auto-calibration of analog clutch paddles (if available)."""
        if self._is_ready():
            try:
                self._send_config_report((0xFF, 0xFF, 0xFF, 1, 0xFF))
            except:
                self.close()

    def recalibrate_battery(self):
        """Force auto-calibration of battery's state of charge (if available)."""
        if self._is_ready():
            try:
                self._send_config_report((0xFF, 0xFF, 0xFF, 2, 0xFF))
            except:
                self.close()

    def reset_buttons_map(self):
        """Return user-defined buttons map to factory defaults.

        No effect if this feature is not supported.
        """
        if self._is_ready():
            try:
                self._send_config_report((0xFF, 0xFF, 0xFF, 3, 0xFF))
            except:
                self.close()

    def save_now(self):
        """Save all user settings to the device's internal flash memory."""
        if self._is_ready():
            try:
                self._send_config_report((0xFF, 0xFF, 0xFF, 4, 0xFF))
            except:
                self.close()

    def get_button_map(self, rawInputNumber: int):
        """Returns a user-defined button mapping.

        Parameters:

            rawInputNumber : A firmware-defined button number in the range from 0 to 63, inclusive.

        Returns an empty dictionary if the requested button number does not exist.
        Otherwise, returns a dictionary with the following keys:

            firmware : The same as the parameter "rawInputNumber".
            user : An user-defined button number in the range from 0 to 127, which will be
                   reported when the button is pressed.
            userAltMode: The same as "user"", but in alternate mode.

        Raises AnotherAppInterferesError if another application is trying to do the same thing.
        The user should try later in such a case.
        """
        if (rawInputNumber < 0) or (rawInputNumber >= 64):
            raise ValueError("rawInputNumber not in the range 0..63")
        if self._is_ready():
            if self.__dataMinorVersion == 0:
                return {}
            try:
                self._send_buttons_map_report((rawInputNumber, 0xFF, 0xFF))
                report = self._get_buttons_map_report()
            except:
                self.close()
                return {}

            if report[0] != rawInputNumber:
                raise AnotherAppInterferesError("Try later")
            elif (
                (report[1] >= 0)
                and (report[1] < 127)
                and (report[2] >= 0)
                and (report[2] < 127)
            ):
                return {
                    "firmware": report[0],
                    "user": report[1],
                    "userAltMode": report[2],
                }
        return {}

    def set_button_map(
        self, rawInputNumber: int, userInputNumber: int, userInputNumberAltMode: int
    ):
        """Sets an user-defined button mapping"""
        if (rawInputNumber < 0) or (rawInputNumber >= 64):
            raise ValueError("rawInputNumber not in the range 0..63")
        if (userInputNumber < 0) or (userInputNumber >= 128):
            raise ValueError("userInputNumber not in the range 0..127")
        if (userInputNumberAltMode < 0) or (userInputNumberAltMode >= 128):
            raise ValueError("userInputNumberAltMode not in the range 0..127")
        if self._is_ready():
            try:
                self._send_buttons_map_report(
                    (rawInputNumber, userInputNumber, userInputNumberAltMode)
                )
            except:
                self.close()

    def set_button_map_tuple(self, tupleOrListOrDict):
        """Sets an user-defined button mapping

        Args:
            tupleOrListOrDict (tuple/list/dict): User-defined button mapping as described below.

        Three items are expected in the given argument:
            Index 0 or key \"firmware\": A firmware-defined button number in the range from 0 to 63, inclusive.
            Index 1 or key \"user\": An user-defined button number in the range from 0 to 127, inclusive.
            Index 2 or key \"userAltMode\": the same as index 1, but for alternate mode.
        """
        if (type(tupleOrListOrDict) == tuple) or (type(tupleOrListOrDict) == list):
            if len(tupleOrListOrDict) == 3:
                self.set_button_map(
                    tupleOrListOrDict[0], tupleOrListOrDict[1], tupleOrListOrDict[2]
                )
        elif type(tupleOrListOrDict) == dict:
            self.set_button_map(
                tupleOrListOrDict["firmware"],
                tupleOrListOrDict["user"],
                tupleOrListOrDict["userAltMode"],
            )

    def enumerate_buttons_map(self):
        """Enumerates all available firmware-defined button numbers and their current user-defined map.

        Remarks:
            May take a few seconds to run.
        """
        for raw in range(64):
            map = self.get_button_map(raw)
            if map != {}:
                yield map

    @property
    def is_user_configurable(self):
        """Returns True if this device has any setting available for user configuration."""
        if self._is_ready():
            return self.has_buttons_map or bool(
                (
                    (1 << _CAP_ALT)
                    | (1 << _CAP_CLUTCH_BUTTON)
                    | (1 << _CAP_CLUTCH_ANALOG)
                    | (1 << _CAP_BATTERY_CALIBRATION_AVAILABLE)
                    | (1 << _CAP_DPAD)
                )
                & self._capabilityFlags
            )
        else:
            return False

    def serialize(self, all: bool = False) -> dict:
        """Returns a dictionary containing current device settings

        Args:
            all (bool, optional): When False, not user-configurable settings are omitted.
            Otherwise, default values are given for those.

        Returns:
            dict: A representation of current user settings

        Remarks:
            May take a few seconds to run.
        """
        result = {}
        if all or self.has_alt_buttons:
            result["AltWorkingMode"] = self.alt_buttons_working_mode
        if all or self.has_dpad:
            result["DpadWorkingMode"] = self.dpad_working_mode
        if all or self.has_clutch:
            result["Clutch"] = [self.clutch_working_mode, self.bite_point]
        if self.has_buttons_map:
            try:
                result["ButtonsMap"] = list(self.enumerate_buttons_map())
            except:
                pass
        elif all:
            result["ButtonsMap"] = [
                {
                    "firmware": i,
                    "user": i,
                    "userAltMode": i + 64,
                }
                for i in range(0, 64)
            ]

        return result

    def deserialize(self, source: dict):
        """Updates device user settings from the given dictionary

        Args:
            source (dict): A dictionary object as returned by serialize()
        """
        if "AltWorkingMode" in source:
            self.alt_buttons_working_mode = source["AltWorkingMode"]
        if "DpadWorkingMode" in source:
            self.dpad_working_mode = source["DpadWorkingMode"]
        if "Clutch" in source:
            self.clutch_working_mode = source["Clutch"][0]
            self.bite_point = source["Clutch"][1]
        if "ButtonsMap" in source:
            buttons_map = source["ButtonsMap"]
            if type(buttons_map) == list:
                for m in buttons_map:
                    self.set_button_map_tuple(m)


###############################################################################


def enumerate(configurableOnly: bool = True):
    """Retrieve all connected ESP32 open-source sim wheels or button boxes.

    Args:
        configurableOnly (bool, optional):
        if True, devices with no user-configurable settings will be ignored.
        Defaults to True.

    Yields:
        SimWheel: A connected ESP32 open-source sim wheel or button box.
    """
    for device_dict in hid.enumerate():
        usage_page = device_dict["usage_page"]
        page = device_dict["usage"]
        if (usage_page == 1) and (page == _CONTROLLER_TYPE):
            aWheel = SimWheel(device_dict["path"])
            test = aWheel.is_sim_wheel and (
                (not configurableOnly) or aWheel.is_user_configurable
            )
            if test:
                yield aWheel


###############################################################################

if __name__ == "__main__":
    for sim_wheel in enumerate(configurableOnly=False):
        print("***********************************************************")
        print(f"Path: {sim_wheel.path}")
        print(f"Manufacturer: {sim_wheel.manufacturer}")
        print(f"Product: {sim_wheel.product_name}")
        print(f"Device ID: {sim_wheel.deviceID}")
        print("Please, wait while loading user settings...")
        print(sim_wheel.serialize(includeButtonsMap=True))
