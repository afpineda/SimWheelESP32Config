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
_RID_PIXEL_CONTROL_ID = 30

# Note: must increase data size in 1 to make room for the report-ID field
_REPORT2_SIZE_V1_0 = 8 + 1
_REPORT2_SIZE_V1_1 = _REPORT2_SIZE_V1_0 + 8
_REPORT2_SIZE_V1_3 = _REPORT2_SIZE_V1_1 + 1
_REPORT2_SIZE_V1_4 = _REPORT2_SIZE_V1_3 + 3

_REPORT3_SIZE_V1_0 = 4 + 1
_REPORT3_SIZE_V1_1 = _REPORT3_SIZE_V1_0 + 1
_REPORT3_SIZE_V1_2 = _REPORT3_SIZE_V1_1 + 1
_REPORT3_SIZE_V1_5 = _REPORT3_SIZE_V1_2 + 1

_REPORT4_SIZE_V1_1 = 3 + 1

_REPORT5_SIZE_V1_2 = 6 + 1

_REPORT30_SIZE_V1_4 = 6 + 1

_MAX_REPORT_SIZE = 25

# Capability flags
_CAP_CLUTCH_BUTTON = 0  # has digital clutch paddles (switches)
_CAP_CLUTCH_ANALOG = 1  # has analog clutch paddles (potentiometers)
_CAP_ALT = 2  # has "ALT" buttons
_CAP_DPAD = 3  # has a directional pad
_CAP_BATTERY = 4  # battery-operated
_CAP_BATTERY_CALIBRATION_AVAILABLE = 5  # has battery calibration data
_CAP_ROTARY_ENCODERS = 10  # has rotary encoders

# Data version
_SUPPORTED_DATA_MAJOR_VERSION = 1
_SUPPORTED_DATA_MINOR_VERSION = 6

# Simple commands
_CMD_AXIS_RECALIBRATE = 1
_CMD_BATT_RECALIBRATE = 2
_CMD_RESET_BUTTONS_MAP = 3
_CMD_SAVE_NOW = 4
_CMD_REVERSE_LEFT_AXIS = 5
_CMD_REVERSE_RIGHT_AXIS = 6
_CMD_SHOW_PIXELS = 7
_CMD_RESET_PIXELS = 8

###############################################################################


class AnotherAppInterferesError(Exception):
    """Raised when another application is interfering in the reading of buttons maps."""

    pass


###############################################################################


class ClutchPaddlesWorkingMode(IntEnum):
    """Working modes of clutch paddles.

    CLUTCH               : F1-style clutch
    AXIS                 : Independent analog axes
    ALT                  : Alternate mode
    BUTTON               : Regular buttons
    LAUNCH_CONTROL_LEFT  : Launch control (left paddle is master)
    LAUNCH_CONTROL_RIGHT : Launch control (right paddle is master)
    """

    CLUTCH = 0
    AXIS = 1
    ALT = 2
    BUTTON = 3
    LAUNCH_CONTROL_LEFT = 4
    LAUNCH_CONTROL_RIGHT = 5


###############################################################################


class PixelGroup(IntEnum):
    """Pixel groups"""

    GRP_TELEMETRY = 0
    GRP_BACKLIGHTS = 1
    GRP_INDIVIDUAL = 2


###############################################################################


class SimWheel:
    """A class to represent an ESP32 open-source sim wheel or button box."""

    def __init__(self, path: str = "", vid: int = 0, pid: int = 0):
        """Create a representation of an ESP32 open-source sim wheel or button box."""
        self._hid = hid.device()
        self.__path = path
        self.__is_open = False
        self.__is_sim_wheel = None
        self.__data_minor_version = None
        self.__data_major_version = None
        self._capability_flags = 0
        self.__vid = vid
        self.__pid = pid
        self.__pixel_count = [0, 0, 0]

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
            data = struct.unpack("<HHHH", report2[1:_REPORT2_SIZE_V1_0])
            check_failed = data[0] != 48977  # Expected magic number
            check_failed = check_failed or (
                data[1] != _SUPPORTED_DATA_MAJOR_VERSION
            )  # Check major version
            check_failed = check_failed or (
                data[2] > _SUPPORTED_DATA_MINOR_VERSION
            )  # Check minor version
            if check_failed:
                return False
            self.__data_major_version = data[1]
            self.__data_minor_version = data[2]
            self._capability_flags = data[3]

            # At data version 1.1, get device ID
            if len(report2) >= _REPORT2_SIZE_V1_1:
                data = struct.unpack(
                    "<Q", report2[_REPORT2_SIZE_V1_0:_REPORT2_SIZE_V1_1]
                )
                self.device_id = data[0]
            else:
                self.device_id = 0

            # At data version 1.3, get max FPS
            if len(report2) >= _REPORT2_SIZE_V1_3:
                data = struct.unpack(
                    "<B", report2[_REPORT2_SIZE_V1_1:_REPORT2_SIZE_V1_3]
                )
                self.max_fps = data[0]
            else:
                self.max_fps = 0

            # At data version 1.4, get pixel count
            if len(report2) >= _REPORT2_SIZE_V1_3:
                data = struct.unpack(
                    "<BBB", report2[_REPORT2_SIZE_V1_3:_REPORT2_SIZE_V1_4]
                )
                self.__pixel_count[PixelGroup.GRP_TELEMETRY] = data[0]
                self.__pixel_count[PixelGroup.GRP_BACKLIGHTS] = data[1]
                self.__pixel_count[PixelGroup.GRP_INDIVIDUAL] = data[2]

            # Confirm the "configuration" report is available
            self._hid.get_feature_report(_RID_CONFIG, _MAX_REPORT_SIZE)

            # At data version 1.1, confirm that additional reports are available
            if (self.__data_major_version == 1) and (self.__data_minor_version >= 1):
                self._hid.get_feature_report(_RID_BUTTONS_MAP, _REPORT4_SIZE_V1_1)

            # At data version 1.2, confirm that additional reports are available
            if (self.__data_major_version == 1) and (self.__data_minor_version >= 2):
                self._hid.get_feature_report(_RID_HARDWARE_ID, _REPORT5_SIZE_V1_2)

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
        if self.__data_minor_version >= 5:
            return struct.unpack("<BBBBBBB", report3[1:_REPORT3_SIZE_V1_5])
        elif self.__data_minor_version >= 2:
            return struct.unpack("<BBBBBB", report3[1:_REPORT3_SIZE_V1_2])
        elif self.__data_minor_version == 1:
            return struct.unpack("<BBBBB", report3[1:_REPORT3_SIZE_V1_1])
        else:
            return struct.unpack("<BBBB", report3[1:_REPORT3_SIZE_V1_0])

    def _send_config_report(self, data: bytes):
        """Writes a device configuration feature report (id #3)."""
        aux = bytearray(_REPORT3_SIZE_V1_5)
        aux[0] = _RID_CONFIG
        aux[1] = data[0]
        aux[2] = data[1]
        aux[3] = data[2]
        aux[4] = data[3]
        if self.__data_minor_version >= 1:
            aux[5] = data[4]
        if self.__data_minor_version >= 2:
            aux[6] = data[5]
        if self.__data_minor_version >= 5:
            aux[7] = data[6]
        if self.__data_minor_version >= 5:
            self._hid.send_feature_report(aux[0:_REPORT3_SIZE_V1_5])
        elif self.__data_minor_version >= 2:
            self._hid.send_feature_report(aux[0:_REPORT3_SIZE_V1_2])
        elif self.__data_minor_version == 1:
            self._hid.send_feature_report(aux[0:_REPORT3_SIZE_V1_1])
        elif self.__data_minor_version == 0:
            self._hid.send_feature_report(aux[0:_REPORT3_SIZE_V1_0])
        else:
            raise RuntimeError("Unsupported data version")

    def _send_simple_command(self, command: int):
        """Send a simple command to the device."""
        if self._is_ready():
            try:
                self._send_config_report(
                    bytes([0xFF, 0xFF, 0xFF, command, 0xFF, 0xFF, 0xFF])
                )
            except Exception:
                self.close()

    def _get_buttons_map_report(self):
        """Read a buttons map feature report (id #4)."""
        if self.__data_minor_version >= 1:
            data = bytes(
                self._hid.get_feature_report(_RID_BUTTONS_MAP, _REPORT4_SIZE_V1_1)
            )
            return struct.unpack("<BBB", data[1:_REPORT4_SIZE_V1_1])
        else:
            return ()

    def _send_buttons_map_report(self, data: bytes):
        """Writes a buttons map feature report."""
        aux = bytearray(_REPORT4_SIZE_V1_1)
        aux[0] = _RID_BUTTONS_MAP
        aux[1] = data[0]
        aux[2] = data[1]
        aux[3] = data[2]
        self._hid.send_feature_report(aux)

    def _send_pixel_control_report(self, data: bytes):
        """Writes a pixel control output report."""
        aux = bytearray(_REPORT30_SIZE_V1_4)
        aux[0] = _RID_PIXEL_CONTROL_ID
        aux[1] = data[0]
        aux[2] = data[1]
        aux[3] = data[2]
        aux[4] = data[3]
        aux[5] = data[4]
        aux[6] = data[5]
        self._hid.write(aux)

    def _get_hardware_id_report(self):
        """Read a custom hardware ID feature report (id #5)."""
        if self.__data_minor_version >= 2:
            data = bytes(
                self._hid.get_feature_report(_RID_HARDWARE_ID, _REPORT5_SIZE_V1_2)
            )
            return struct.unpack("<HHH", data[1:7])
        else:
            return ()

    def _send_hardware_id_report(self, data: bytes):
        """Writes a custom hardware ID feature report."""
        aux = bytearray(_REPORT5_SIZE_V1_2)
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
    def has_pixel_control(self) -> bool:
        """Returns True if this device has pixels."""
        self._open()
        return (
            (self.__pixel_count[PixelGroup.GRP_TELEMETRY] > 0)
            or (self.__pixel_count[PixelGroup.GRP_BACKLIGHTS] > 0)
            or (self.__pixel_count[PixelGroup.GRP_INDIVIDUAL] > 0)
        )

    @property
    def has_battery(self) -> bool:
        """Returns True if this device is powered by batteries."""
        if self._is_ready():
            return bool((1 << _CAP_BATTERY) & self._capability_flags)
        else:
            return False

    @property
    def has_rotary_encoders(self) -> bool:
        """Returns True if this device has configurable rotary encoders."""
        if self._is_ready():
            return bool((1 << _CAP_ROTARY_ENCODERS) & self._capability_flags)
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
    def battery_soc(self) -> int | None:
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
                    bytes([int(mode), 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
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
                    bytes([0xFF, int(mode), 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
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
                    bytes([0xFF, 0xFF, value, 0xFF, 0xFF, 0xFF, 0xFF])
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
                    bytes([0xFF, 0xFF, 0xFF, 0xFF, int(mode), 0xFF, 0xFF])
                )
            except Exception:
                self.close()

    @property
    def vid(self) -> str:
        """Current Vendor ID."""
        return self.__vid

    @property
    def pid(self) -> str:
        """Current Product ID."""
        return self.__pid

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
        """Custom VID for this device.

        Effective after next reboot.
        """
        if self._is_ready():
            try:
                report = self._get_hardware_id_report()
                return report[0]
            except Exception:
                self.close()
        return None

    @property
    def custom_pid(self) -> int | None:
        """Custom PID for this device.

        Effective after next reboot.
        """
        if self._is_ready():
            try:
                report = self._get_hardware_id_report()
                return report[1]
            except Exception:
                self.close()
        return None

    @property
    def pulse_width_multiplier(self) -> int:
        """Pulse width multiplier for rotary encoders."""
        try:
            report = self._get_config_report()
            if len(report) >= 7:
                return int(report[6])
            else:
                return 1
        except Exception:
            self.close()
            return 1

    @pulse_width_multiplier.setter
    def pulse_width_multiplier(self, value: int):
        if self._is_ready():
            try:
                self._send_config_report(
                    bytes([0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, int(value)])
                )
            except Exception:
                self.close()

    def recalibrate_analog_axes(self):
        """Force auto-calibration of analog clutch paddles (if available)."""
        self._send_simple_command(_CMD_AXIS_RECALIBRATE)

    def recalibrate_battery(self):
        """Force auto-calibration of battery's state of charge (if available)."""
        self._send_simple_command(_CMD_BATT_RECALIBRATE)

    def reset_buttons_map(self):
        """Return user-defined buttons map to factory defaults.

        No effect if this feature is not supported.
        """
        self._send_simple_command(_CMD_RESET_BUTTONS_MAP)

    def save_now(self):
        """Save all user settings to the device's internal flash memory."""
        self._send_simple_command(_CMD_SAVE_NOW)

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

    def reverse_left_axis(self):
        """Reverse the polarity of the left analog axis."""
        self._send_simple_command(_CMD_REVERSE_LEFT_AXIS)

    def reverse_right_axis(self):
        """Reverse the polarity of the right analog axis."""
        self._send_simple_command(_CMD_REVERSE_RIGHT_AXIS)

    def pixel_count(self, group: PixelGroup) -> int:
        """Number of pixels in a group"""
        return self.__pixel_count[group]

    def pixel_set(
        self, group: PixelGroup, index: int, red: int, green: int, blue: int
    ) -> None:
        """Set pixel color in a group"""
        if (
            self._is_ready()
            and (group < 3)
            and (index >= 0)
            and (index < self.__pixel_count[group])
        ):
            try:
                self._send_pixel_control_report(
                    bytes([group, index, blue, green, red, 0x00])
                )
            except Exception:
                self.close()

    def pixel_show(self) -> None:
        """Show all pixels (in all groups) at once"""
        if self._is_ready():
            try:
                if self.data_minor_version >= 6:
                    self._send_pixel_control_report(
                        bytes([0xFF, 0x00, 0x00, 0x00, 0x00, 0x00])
                    )
                else:
                    self._send_simple_command(_CMD_SHOW_PIXELS)

            except Exception:
                self.close()

    def pixel_reset(self) -> None:
        """Turn off all pixels (in all groups) at once"""
        if self._is_ready():
            try:
                if self.data_minor_version >= 6:
                    self._send_pixel_control_report(
                        bytes([0xFE, 0x00, 0x00, 0x00, 0x00, 0x00])
                    )
                else:
                    self._send_simple_command(_CMD_RESET_PIXELS)

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
        path = device_dict["path"]
        vid = device_dict["vendor_id"]
        pid = device_dict["product_id"]
        if (usage_page == 1) and (page == _CONTROLLER_TYPE):
            a_wheel = SimWheel(path, vid, pid)
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
        print(f"Current VID: {hex(sim_wheel.vid)}")
        print(f"Current PID: {hex(sim_wheel.pid)}")
        print(f"Manufacturer: {sim_wheel.manufacturer}")
        print(f"Product: {sim_wheel.product_name}")
        print(f"Device ID: {hex(sim_wheel.device_id)}")
        print(f"Allow custom HW ID: {sim_wheel.has_custom_hw_id}")
        print(f"Custom VID: {hex(sim_wheel.custom_vid)}")
        print(f"Custom PID: {hex(sim_wheel.custom_pid)}")
        print(f"Security lock: {sim_wheel.is_read_only}")
        print(f"Battery: {sim_wheel.has_battery}")
        print(f"Battery calibration data: {sim_wheel.battery_calibration_available}")
        print(f"Battery SOC: {sim_wheel.battery_soc}")
        print(f"Rotary encoders: {sim_wheel.has_rotary_encoders}")
        print(f"Max FPS: {sim_wheel.max_fps}")
        tel_pc = sim_wheel.pixel_count(PixelGroup.GRP_TELEMETRY)
        bck_pc = sim_wheel.pixel_count(PixelGroup.GRP_BACKLIGHTS)
        ind_pc = sim_wheel.pixel_count(PixelGroup.GRP_INDIVIDUAL)
        print(f"Led count {tel_pc} / {bck_pc} / {ind_pc}")
        sim_wheel.pixel_set(PixelGroup.GRP_TELEMETRY,0,255,0,0);
        sim_wheel.pixel_set(PixelGroup.GRP_BACKLIGHTS,0,255,0,0);
        sim_wheel.pixel_set(PixelGroup.GRP_INDIVIDUAL,0,255,0,0);
        sim_wheel.pixel_show()
        print(f"Pulse width multiplier: {sim_wheel.pulse_width_multiplier}")
        print("Please, wait while loading user settings...")
        print(sim_wheel.serialize(all=True))
        sim_wheel.pixel_reset()
    print("Done.")
