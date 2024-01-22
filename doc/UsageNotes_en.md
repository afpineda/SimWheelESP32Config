# Usage notes

## Startup

At startup, connected devices will be automatically scanned.
When found, the app will connect to the first available one.

Note that bluetooth devices **must be paired** first
in order for this app to detect them.

## Select another sim wheel / button box

Click on the "drawer" button on the top-left corner.
Available devices will be automatically scanned and listed.
If your device is not connected yet, connect it, wait a second, and
click on the "refresh" button.

Note that devices with no user-configurable settings will never show up.

Click on the "Select" button in order to connect to that device.

## User settings

Only **user-configurable** settings will show up, which depends on your device capabilities.

## "Buttons map"

- Click "Reload" to download current map from the device (may take a few seconds).
- Changes are immediately applied, but **not** automatically saved to the device.
- Click "Save" to make any change available after power off.
- Click "Defaults" to revert to "factory defaults".
- Button numbers are 0-based. For example, button #0 is the first button.
  Note that the following button numbers have a special meaning in Windows:
  - *00*: "A" button
  - *01*: "B" button
  - *02*: "X" button
  - *03*: "Y" button
  - *04*: "LB" button (should be reserved for the left shift paddle)
  - *05*: "RB" button (should be reserved for the right shift paddle)
  - *06*: "Back" button
  - *07*: "Start" button.
- "Firmware-defined" button numbers are fixed and hardware-dependant.
- The "user-defined" button number is reported to the hosting PC when the
  corresponding "firmware-defined" button is pressed.
  By default, this is the same as the "firmware-defined" button number.
- The "user-defined" button number in "alt mode" is reported to the hosting PC when the
  corresponding "firmware-defined" button is pressed and "alternate mode" is engaged.
  By default, this is the same as the "firmware-defined" button number plus 64.
- Any user-defined button number is in the range from 0 to 127 (inclusive), which is the absolute maximum
  count of buttons supported by the operating system.
