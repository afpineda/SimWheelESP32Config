# Change log

## 2.7.0

- Support for custom pulse width multipliers for rotary encoders.
- Up to date with data version 1.5 (firmware version 6.11.0).

## 2.6.0

- Support for "Launch control" (firmware version 6.10.0).

## 2.5.0

- Updated to work with data version 1.4 (firmware version 6.4.0)
- No new features.
- From now on, this changelog is written in reverse order.

## 2.4.0

- Show current VID and PID on device listing.
- Updated to work with data version 1.3.

## 2.3.0

- Added two buttons in order to reverse axis polarity (in analog clutch paddles only).

## 2.2.0

- Updated to work with data version 1.2.
- On BLE devices you may set a custom VID, PID (Windows/Linux/Mac) and/or display name (Windows only).
- Bug fixes.
- Updated documentation.

## 2.1.2

- Fixed bug which caused an app crash at startup when using certain character encodings in the text terminal
  (used for logging purposes). No new functionalities.
- Fixed incomplete installation instructions for Linux users.

## 2.1.1

- Rebuild due to a [bug](https://github.com/afpineda/appstrings-python/issues/1) in library "appstrings".
  Thanks to user [Aalexz](https://github.com/Aalexz).No new functionalities.
- Minor changes for [SonarLint](https://docs.sonarsource.com/sonarlint/vs-code/) compliance.

## 2.1.0

- Added Chinese language.
- Added command-line parameter to force any available user language.
- Code revision with SonarLint.

## 2.0.1

- License has changed to EUPL 1.2
- Implementation now uses `appstrings` library from this author.
- No changes in functionality, so there is no release for this version.

## 2.0.0

- Moving to Python implementation.
- A change in the settings through the hardware itself is
  automatically reflected in the app without a explicit refresh.
- Backwards-compatible: support for 1.0 and 1.1 data versions.

## 1.3.0

- Handle multiple devices available at the same time.
- Minor bug fixes.

## 1.2.0

- Updated to data version 1.1.
- Select DPAD working mode.
- User-defined buttons map.

## 1.1.0

- Ignore devices with no available configuration options.
- Added some usage notes.

## 1.0.0

- First release with basic functionality.
- Windows only. Delphi implementation.
