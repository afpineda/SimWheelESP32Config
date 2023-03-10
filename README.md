# Configuration app for ESP32 based open source sim wheels

A companion app for [ESP32 based open source wireless steering wheel](https://github.com/afpineda/OpenSourceSimWheelESP32).

![Screenshot](./resources/Screenshot.png)

[Usage notes](./doc/UsageNotes_en.md)

## Features

- Load/save settings.
- Select working mode of clutch paddles.
- Select working mode of "ALT" buttons.
- Set clutch bite point.
- Force auto-calibration of analog clutch paddles.
- Force battery auto-calibration. Not available if the battery was previously calibrated.
- Windows 64 bits only.

## Change log

### 1.0.0

- First release with basic functionality.
- Windows only. Delphi implementation.

### 1.1.0

- Ignore devices with no available configuration options.
- Added some usage notes.

## Future improvements

Note: **NOT GUARANTEED**

- *Electron.js* implementation for portability.

- Auto-detect game and car in order to apply a preset.

- Store presets into a Sqlite database.
