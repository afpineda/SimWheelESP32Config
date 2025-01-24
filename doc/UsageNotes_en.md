# Usage notes

## Startup

At startup, connected devices will be automatically scanned.
When found, the app will connect to the first available one.

Note that Bluetooth devices **must be paired** first
in order for this app to detect them.

## Select another sim wheel / button box

Click on the "drawer" button on the top-left corner.
Available devices will be automatically scanned and listed.
If your device is not connected yet, connect it, wait a second, and
click on the `🔄 Refresh` button.

Note that devices with no user-configurable settings will never show up.

Click on the `✅ Select` button in order to connect to that device.

## User settings

Only **user-configurable** settings will show up,
which depends on your device capabilities.

## Security lock

You can activate or deactivate the security lock on your device
by pressing a specific combination of buttons.
This program will display a warning,
and any attempt to modify the configuration will be unsuccessful
if the security lock is activated.

## Pulse width multiplier for rotary encoders

A low value increases the probability of missed rotations on the host computer,
but decreases the probability of missed rotations on the device
when several consecutive rotations are accumulated.
A high value has the opposite effect.

Increase it if the host computer loses rotations occasionally,
but keep it as low as possible.

## Button map

- Click `🔄 Reload` to download the current map from the device (may take a few seconds).
- Changes are applied immediately,
  but **not** saved automatically.
- Click `💾 Save` to make any changes available after power off.
- Click `🏭 Defaults` to revert to "factory defaults".
- Button #0 is the first button.
  Note that the following button numbers have a special meaning in Windows:
  - *00*: "A" button
  - *01*: "B" button
  - *02*: "X" button
  - *03*: "Y" button
  - *04*: "LB" button (should be reserved for the left shift paddle)
  - *05*: "RB" button (should be reserved for the right shift paddle)
  - *06*: "Back" button
  - *07*: "Start" button.
- The "Firmware-defined" button numbers are fixed and depend on the hardware.
- The "user-defined" button number is sent to the hosting PC when the
  corresponding "firmware-defined" button is pressed.
  By default, this is the same as the "firmware-defined" button number.
- The "user-defined" button number in "alt mode" is reported to the hosting PC when the
  corresponding "firmware-defined" button is pressed and the *alternate mode* is engaged.
  By default, this is equal to the "firmware-defined" button number plus 64.
- Each user-defined button number ranges from 0 to 127 (inclusive).

## Custom hardware ID and display name

Available on Bluetooth devices only.

If you have two or more BLE devices using ESP32 open simwheel firmware,
**all of them will show the same display name, because they share the same hardware ID**.

If you need two or more devices to exhibit a different display name,
provide a custom PID (**recommended**), VID, or both.
You may use the existing VID and PID from another non-related device.
However, this is not recommended.

You may set a custom **display name** for all devices sharing the given VID and PID.
If you clear the display name, a generic one will show on the next computer reboot.
**Be warned: you could rename other non-related devices**.
