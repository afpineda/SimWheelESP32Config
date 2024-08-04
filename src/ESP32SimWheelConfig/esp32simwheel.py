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
_RID_HARDWARE_ID = 5

# Note: must increase data size in 1 to make room for the report-ID field

_REPORT_SIZE_CAPABILITIES = 16 + 1
_REPORT_SIZE_CONFIG = 6 + 1
_REPORT_SIZE_BUTTONS_MAP = 3 + 1
_REPORT_SIZE_HARDWARE_ID = 6 + 1
_MAX_REPORT_SIZE = 25

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
        self.__data_minor_version = None
        self.__data_major_version = None
        self._capability_flags = 0

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
            except Exception:
                self.__is_open = False

    # noinspection python:S3776
    def _check_is_sim_wheel(self) -> bool:  # NOSONAR
        """Determine if this device is a supported ESP32 open-source sim wheel or not."""
        # Supported data versions: 1.0, 1.1, 1.2
        try:
            # Get "capabilities" report (ID #2)
            report2 = bytes(
                self._hid.get_feature_report(_RID_CAPABILITIES, _MAX_REPORT_SIZE)
            )

            # Get magic number, data version and flags
            data = struct.unpack("<HHHH", report2[1:9])
            check_failed = data[0] != 48977  # Expected magic number
            check_failed = check_failed or (data[1] != 1)  # Check major version
            check_failed = check_failed or (data[2] > 2)  # Check minor version
            if check_failed:
                return False
            self.__data_major_version = data[1]
            self.__data_minor_version = data[2]
            self._capability_flags = data[3]

            # Reject unsupported (future) versions
            if (self.__data_major_version != 1) or (self.__data_minor_version > 2):
                return False

            # At data version 1.1, get device ID
            if len(report2) >= 17:
                data = struct.unpack("<Q", report2[9:17])
                self.device_id = data[0]
            else:
                self.device_id = 0
            # Confirm the "configuration" report is available
            self._hid.get_feature_report(_RID_CONFIG, _MAX_REPORT_SIZE)

            # At data version 1.1, confirm that additional reports are available
            if (self.__data_major_version == 1) and (self.__data_minor_version >= 1):
                self._hid.get_feature_report(_RID_BUTTONS_MAP, _REPORT_SIZE_BUTTONS_MAP)

            # At data version 1.2, confirm that additional reports are available
            if (self.__data_major_version == 1) and (self.__data_minor_version >= 2):
                self._hid.get_feature_report(_RID_HARDWARE_ID, _REPORT_SIZE_HARDWARE_ID)

            # Check availability of custom hardware ID
            if (self.__data_major_version == 1) and (self.__data_minor_version >= 2):
                report5 = self._get_hardware_id_report()
                self._custom_hw_id_enabled = (report5[0] != 0) or (report5[1] != 0)
            else:
                self._custom_hw_id_enabled = False

            return True
        except Exception:
            return False

    def _get_config_report(self):
        """Read a device configuration feature report (id #3)."""
        report3 = bytes(self._hid.get_feature_report(_RID_CONFIG, _MAX_REPORT_SIZE))
        if self.__data_minor_version >= 2:
            return struct.unpack("<BBBBBB", report3[1:7])
        if self.__data_minor_version >= 1:
            return struct.unpack("<BBBBB", report3[1:6])
        else:
            return struct.unpack("<BBBB", report3[1:5])

    def _send_config_report(self, data: bytes):
        """Writes a device configuration feature report (id #3)."""
        aux = bytearray(_REPORT_SIZE_CONFIG)
        aux[0] = _RID_CONFIG
        aux[1] = data[0]
        aux[2] = data[1]
        aux[3] = data[2]
        aux[4] = data[3]
        if self.__data_minor_version >= 1:
            aux[5] = data[4]
        if self.__data_minor_version >= 2:
            aux[6] = data[5]
        if self.__data_minor_version == 2:
            self._hid.send_feature_report(aux[0:7])
        elif self.__data_minor_version == 1:
            self._hid.send_feature_report(aux[0:6])
        elif self.__data_minor_version == 0:
            self._hid.send_feature_report(aux[0:5])
        else:
            raise RuntimeError("Unsupported data version")

    def _get_buttons_map_report(self):
        """Read a buttons map feature report (id #4)."""
        if self.__data_minor_version >= 1:
            data = bytes(
                self._hid.get_feature_report(_RID_BUTTONS_MAP, _REPORT_SIZE_BUTTONS_MAP)
            )
            return struct.unpack("<BBB", data[1:4])
        else:
            return ()

    def _send_buttons_map_report(self, data: bytes):
        """Writes a buttons map feature report."""
        aux = bytearray(_REPORT_SIZE_BUTTONS_MAP)
        aux[0] = _RID_BUTTONS_MAP
        aux[1] = data[0]
        aux[2] = data[1]
        aux[3] = data[2]
        self._hid.send_feature_report(aux)

    def _get_hardware_id_report(self):
        """Read a custom hardware ID feature report (id #5)."""
        if self.__data_minor_version >= 2:
            data = bytes(
                self._hid.get_feature_report(_RID_HARDWARE_ID, _REPORT_SIZE_HARDWARE_ID)
            )
            return struct.unpack("<HHH", data[1:7])
        else:
            return ()

    def _send_hardware_id_report(self, data: bytes):
        """Writes a custom hardware ID feature report."""
        aux = bytearray(_REPORT_SIZE_HARDWARE_ID)
        aux[0] = _RID_HARDWARE_ID
        aux[1] = data[0]
        aux[2] = data[1]
        aux[3] = data[2]
        aux[4] = data[3]
        aux[5] = data[4]
        aux[6] = data[5]
        self._hid.send_feature_report(aux)

    def _is_ready(self):
        """Returns True if the device is connected and ready for user configuration."""
        self._open()
        return (self.__is_sim_wheel == True) and (self.__is_open)

    def close(self):
        """Close HID connection."""
        try:
            self._hid.close()
        except Exception:
            pass
        self.__is_open = False

    @property
    def is_alive(self) -> bool:
        """Returns True if this device is still connected"""
        self._open()
        try:
            self._get_config_report()
        except Exception:
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
            return self.__data_minor_version >= 1
        else:
            return False

    @property
    def has_clutch(self) -> bool:
        """Returns True if this device has clutch paddles (any kind)."""
        if self._is_ready():
            return bool(
                ((1 << _CAP_CLUTCH_ANALOG) | (1 << _CAP_CLUTCH_BUTTON))
                & self._capability_flags
            )
        else:
            return False

    @property
    def has_analog_clutch_paddles(self) -> bool:
        """Returns True if this device has analog clutch paddles."""
        if self._is_ready():
            return bool((1 << _CAP_CLUTCH_ANALOG) & self._capability_flags)
        else:
            return False

    @property
    def has_dpad(self) -> bool:
        """Returns True if this device has navigational controls."""
        if self._is_ready():
            return bool((1 << _CAP_DPAD) & self._capability_flags)
        else:
            return False

    @property
    def has_alt_buttons(self) -> bool:
        """Returns True if this device has ALT buttons."""
        if self._is_ready():
            return bool((1 << _CAP_ALT) & self._capability_flags)
        else:
            return False

    @property
    def has_battery(self) -> bool:
        """Returns True if this device is powered by batteries."""
        if self._is_ready():
            return bool((1 << _CAP_BATTERY) & self._capability_flags)
        else:
            return False

    @property
    def battery_calibration_available(self) -> bool:
        """Returns True if this device is able to auto-calibrate battery's state of charge."""
        if self._is_ready():
            return bool(
                (1 << _CAP_BATTERY_CALIBRATION_AVAILABLE) & self._capability_flags
            )
        else:
            return False

    @property
    def batter_soc(self) -> int | None:
        """Returns a percentage (0..100) of current battery charge"""
        if self._is_ready():
            try:
                report = self._get_config_report()
                return report[3]
            except Exception:
                self.close()
        return None

    @property
    def data_major_version(self) -> int | None:
        """Major version of the data interchange specification supported by this device."""
        return self.__data_major_version

    @property
    def data_minor_version(self) -> int | None:
        """Minor version of the data interchange specification supported by this device."""
        return self.__data_minor_version

    @property
    def clutch_working_mode(self) -> ClutchPaddlesWorkingMode | None:
        """Returns the current working mode of clutch paddles.

        This value has no meaning if there are no clutch paddles.
        Check has_clutch_paddles first.
        """
        if self._is_ready():
            try:
                report = self._get_config_report()
                return ClutchPaddlesWorkingMode(report[0])
            except Exception:
                self.close()
        return None

    @clutch_working_mode.setter
    def clutch_working_mode(self, mode: ClutchPaddlesWorkingMode):
        """Set the working mode of clutch paddles.

        No effect if there are no clutch paddles.
        """
        if self._is_ready():
            try:
                self._send_config_report(
                    bytes([int(mode), 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
                )
            except Exception:
                self.close()

    @property
    def alt_buttons_working_mode(self) -> bool | None:
        """Returns the working mode of ALT buttons.

        True for alternate mode, False for regular buttons mode.
        This value has no meaning if there are no ALT buttons.
        Check has_alt_buttons first.
        """
        if self._is_ready():
            try:
                report = self._get_config_report()
                return bool(report[1])
            except Exception:
                self.close()
        return None

    @alt_buttons_working_mode.setter
    def alt_buttons_working_mode(self, mode: bool):
        """Set the working mode of ALT buttons.

        No effect if there are no ALT buttons.
        """
        if self._is_ready():
            try:
                self._send_config_report(
                    bytes([0xFF, int(mode), 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
                )
            except Exception:
                self.close()

    @property
    def bite_point(self) -> int | None:
        """Returns the current clutch's bite point.

        A value in the range from 0 to 254, inclusive.
        Non-meaningful if there are no clutch paddles.
        """
        if self._is_ready():
            try:
                report = self._get_config_report()
                return report[2]
            except Exception:
                self.close()
        return None

    @bite_point.setter
    def bite_point(self, value: int):
        """Sets the clutch's bite point.

        No effect if there are no clutch paddles.
        """
        if (value < 0) or (value > 254):
            raise ValueError("Bite point not in the range 0..254")
        if self._is_ready():
            try:
                self._send_config_report(
                    bytes([0xFF, 0xFF, value, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
                )
            except Exception:
                self.close()

    @property
    def dpad_working_mode(self) -> bool | None:
        """Returns the working mode of navigational controls.

        True for navigation, False for regular buttons mode.
        This value has no meaning if there are no navigational controls.
        Check has_dpad first.
        """
        if self._is_ready():
            try:
                report = self._get_config_report()
                return bool(report[4])
            except Exception:
                self.close()
        return None

    @dpad_working_mode.setter
    def dpad_working_mode(self, mode: bool):
        """Set the working mode of navigational controls.

        No effect if there are no navigational controls.
        """
        if self._is_ready():
            try:
                self._send_config_report(
                    bytes([0xFF, 0xFF, 0xFF, 0xFF, int(mode), 0xFF, 0xFF, 0xFF, 0xFF])
                )
            except Exception:
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

    @property
    def is_user_configurable(self) -> bool:
        """Returns True if this device has any setting available for user configuration."""
        if self._is_ready():
            return (
                self.has_buttons_map
                or self.has_custom_hw_id
                or bool(
                    (
                        (1 << _CAP_ALT)
                        | (1 << _CAP_CLUTCH_BUTTON)
                        | (1 << _CAP_CLUTCH_ANALOG)
                        | (1 << _CAP_BATTERY_CALIBRATION_AVAILABLE)
                        | (1 << _CAP_DPAD)
                    )
                    & self._capability_flags
                )
            )
        else:
            return False

    @property
    def is_read_only(self) -> bool:
        """Security lock on this device."""
        if self._is_ready() and (self.__data_minor_version >= 2):
            try:
                report3 = bytes(
                    self._hid.get_feature_report(_RID_CONFIG, _MAX_REPORT_SIZE)
                )
                return report3[6] != 0
            except Exception:
                self.close()
        return False

    @property
    def has_custom_hw_id(self) -> bool:
        """Check if this device can set a custom hardware ID"""
        if self._is_ready():
            return self._custom_hw_id_enabled
        else:
            return False

    @property
    def custom_vid(self) -> int | None:
        """Custom VID for this device"""
        if self._is_ready():
            try:
                report = self._get_hardware_id_report()
                return report[0]
            except Exception:
                self.close()
        return None

    @property
    def custom_pid(self) -> int | None:
        """Custom VID for this device"""
        if self._is_ready():
            try:
                report = self._get_hardware_id_report()
                return report[1]
            except Exception:
                self.close()
        return None

    def recalibrate_analog_axes(self):
        """Force auto-calibration of analog clutch paddles (if available)."""
        if self._is_ready():
            try:
                self._send_config_report(
                    bytes([0xFF, 0xFF, 0xFF, 1, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
                )
            except Exception:
                self.close()

    def recalibrate_battery(self):
        """Force auto-calibration of battery's state of charge (if available)."""
        if self._is_ready():
            try:
                self._send_config_report(
                    bytes([0xFF, 0xFF, 0xFF, 2, 0xFF, 0xFFFF, 0xFFFF])
                )
            except Exception:
                self.close()

    def reset_buttons_map(self):
        """Return user-defined buttons map to factory defaults.

        No effect if this feature is not supported.
        """
        if self._is_ready():
            try:
                self._send_config_report(
                    bytes([0xFF, 0xFF, 0xFF, 3, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
                )
            except Exception:
                self.close()

    def save_now(self):
        """Save all user settings to the device's internal flash memory."""
        if self._is_ready():
            try:
                self._send_config_report(
                    bytes([0xFF, 0xFF, 0xFF, 4, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
                )
            except Exception:
                self.close()

    def get_button_map(self, raw_input_number: int):
        """Returns a user-defined button mapping.

        Parameters:

            raw_input_number : A firmware-defined button number in the range from 0 to 63, inclusive.

        Returns an empty dictionary if the requested button number does not exist.
        Otherwise, returns a dictionary with the following keys:

            firmware : The same as the parameter "rawInputNumber".
            user : An user-defined button number in the range from 0 to 127, which will be
                   reported when the button is pressed.
            userAltMode: The same as "user"", but in alternate mode.

        Raises AnotherAppInterferesError if another application is trying to do the same thing.
        The user should try later in such a case.
        """
        if (raw_input_number < 0) or (raw_input_number >= 64):
            raise ValueError("rawInputNumber not in the range 0..63")
        if self._is_ready():
            if self.__data_minor_version == 0:
                return {}
            try:
                self._send_buttons_map_report(bytes([raw_input_number, 0xFF, 0xFF]))
                report = self._get_buttons_map_report()
            except Exception:
                self.close()
                return {}

            if report[0] != raw_input_number:
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
        self,
        raw_input_number: int,
        user_input_number: int,
        user_input_number_alt_mode: int,
    ):
        """Sets an user-defined button mapping"""
        if (raw_input_number < 0) or (raw_input_number >= 64):
            raise ValueError("raw_input_number not in the range 0..63")
        if (user_input_number < 0) or (user_input_number >= 128):
            raise ValueError("user_input_number not in the range 0..127")
        if (user_input_number_alt_mode < 0) or (user_input_number_alt_mode >= 128):
            raise ValueError("user_input_number_alt_mode not in the range 0..127")
        if self._is_ready():
            try:
                self._send_buttons_map_report(
                    bytes(
                        [
                            raw_input_number,
                            user_input_number,
                            user_input_number_alt_mode,
                        ]
                    )
                )
            except Exception:
                self.close()

    def set_button_map_tuple(self, tuple_or_list_or_dict):
        """Sets an user-defined button mapping

        Args:
            tuple_or_list_or_dict (tuple/list/dict): User-defined button mapping as described below.

        Three items are expected in the given argument:
            Index 0 or key \"firmware\": A firmware-defined button number in the range from 0 to 63, inclusive.
            Index 1 or key \"user\": An user-defined button number in the range from 0 to 127, inclusive.
            Index 2 or key \"userAltMode\": the same as index 1, but for alternate mode.
        """
        if isinstance(tuple_or_list_or_dict, (tuple, list)):
            if len(tuple_or_list_or_dict) == 3:
                self.set_button_map(
                    tuple_or_list_or_dict[0],
                    tuple_or_list_or_dict[1],
                    tuple_or_list_or_dict[2],
                )
        elif isinstance(tuple_or_list_or_dict, dict):
            self.set_button_map(
                tuple_or_list_or_dict["firmware"],
                tuple_or_list_or_dict["user"],
                tuple_or_list_or_dict["userAltMode"],
            )

    def enumerate_buttons_map(self):
        """Enumerates all available firmware-defined button numbers and their current user-defined map.

        Remarks:
            May take a few seconds to run.
        """
        for raw in range(64):
            btn_map = self.get_button_map(raw)
            if btn_map != {}:
                yield btn_map

    def reset_custom_hardware_id(self):
        """Reset custom hardware ID to factory defaults after next reboot (BLE only)"""
        if self._is_ready():
            try:
                self._send_hardware_id_report(
                    bytes(
                        [
                            0x00,
                            0x00,
                            0x00,
                            0x00,
                            0x96,
                            0xAA,
                        ]
                    )
                )
            except Exception:
                self.close()

    def set_custom_hardware_id(self, vid: int, pid: int):
        """Force a custom hardware ID after next reboot (BLE only)

        Parameters:

            vid : Vendor ID in the range 1..0xFFFF.
            pid : Product ID in the range 1..0xFFFF.
        """
        if (pid <= 0) or (pid > 0xFFFF) or (vid <= 0) or (vid > 0xFFFF):
            raise ValueError("Custom PID/VID not in the range 1..0xFFFF")
        if self._is_ready():
            try:
                control = (vid * pid) % 65536
                vid_bytes = vid.to_bytes(2, byteorder="little")
                pid_bytes = pid.to_bytes(2, byteorder="little")
                control_bytes = control.to_bytes(2, byteorder="little")
                # for debug: print(
                #     f"Request for custom hardware ID: VID = {vid} PID = {pid}, control = {control} "
                # )
                # print(f"(bytes): VID = {vid_bytes[0]},{vid_bytes[1]}")
                # print(f"(bytes): PID = {pid_bytes[0]},{pid_bytes[1]}")
                # print(f"(bytes): control = {control_bytes[0]},{control_bytes[1]}")
                self._send_hardware_id_report(
                    bytes(
                        [
                            vid_bytes[0],
                            vid_bytes[1],
                            pid_bytes[0],
                            pid_bytes[1],
                            control_bytes[0],
                            control_bytes[1],
                        ]
                    )
                )
            except Exception:
                self.close()

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
            except Exception:
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
            if isinstance(buttons_map, list):
                for m in buttons_map:
                    self.set_button_map_tuple(m)


###############################################################################


def enumerate(configurable_only: bool = True):
    """Retrieve all connected ESP32 open-source sim wheels or button boxes.

    Args:
        configurable_only (bool, optional):
        if True, devices with no user-configurable settings will be ignored.
        Defaults to True.

    Yields:
        SimWheel: A connected ESP32 open-source sim wheel or button box.
    """
    for device_dict in hid.enumerate():
        usage_page = device_dict["usage_page"]
        page = device_dict["usage"]
        if (usage_page == 1) and (page == _CONTROLLER_TYPE):
            a_wheel = SimWheel(device_dict["path"])
            test = a_wheel.is_sim_wheel and (
                (not configurable_only) or a_wheel.is_user_configurable
            )
            if test:
                yield a_wheel


###############################################################################

if __name__ == "__main__":
    for sim_wheel in enumerate(configurable_only=False):
        print("***********************************************************")
        print(f"Path: {sim_wheel.path}")
        print(f"Manufacturer: {sim_wheel.manufacturer}")
        print(f"Product: {sim_wheel.product_name}")
        print(f"Device ID: {sim_wheel.device_id}")
        print(f"Allow custom HW ID: {sim_wheel.has_custom_hw_id}")
        print(f"Custom VID: {sim_wheel.custom_vid}")
        print(f"Custom PID: {sim_wheel.custom_pid}")
        print(f"Security lock: {sim_wheel.is_read_only}")
        print("Please, wait while loading user settings...")
        print(sim_wheel.serialize(all=True))
