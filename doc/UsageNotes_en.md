# Usage notes

There are 6 tabs in the app. However, any configuration option not relevant to your device will not show up:

- "Devices" tab: device status and scanning.
- "Clutch paddles" tab": configure the working mode of clutch paddles.
- "ALT buttons" tab: configure the working mode of "ALT" buttons.
- "Battery" tab: show state of charge. If your battery is not calibrated, you may request a battery auto-calibration.
- "Presets" tab: load/save all configuration options.
- "Buttons map" tab: customize button numbers.

If you change any configuration option through the device itself, select another tab for a refresh.

## "Devices" tab

- On start, the app will try to connect to the first available device.
- Hit "Scan" to rescan available devices and connect.
- Incompatible devices will be ignored in the future (there are no incompatible devices right now).
  If that were your case, use an older version of this app or update your firmware.
- Devices with no available configuration options will be ignored (e.g., button boxes).
- **If there are two or more suitable devices, no connection will be made**.
  Since there is no sense in using two (or more) sim wheels at the same time, disconnect one of them.

## "Buttons map" tab

- Changes are **not** automatically saved.
- Click "save" to make any change available after power off.
- Click "Defaults" to return to "factory defaults" (not saved).
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
