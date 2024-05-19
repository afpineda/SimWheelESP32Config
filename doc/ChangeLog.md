# Change log

## 1.0.0

- First release with basic functionality.
- Windows only. Delphi implementation.

## 1.1.0

- Ignore devices with no available configuration options.
- Added some usage notes.

## 1.2.0

- Updated to data version 1.1.
- Select DPAD working mode.
- User-defined buttons map.

## 1.3.0

- Handle multiple devices available at the same time.
- Minor bug fixes.

## 2.0.0

- Moving to Python implementation.
- A change in the settings through the hardware itself is
  automatically reflected in the app without a explicit refresh.
- Backwards-compatible: support for 1.0 and 1.1 data versions.

## 2.0.1

- License has changed to EUPL 1.2
- Implementation now uses `appstrings` library from this author.
- No changes in functionality, so there is no release for this version.

## 2.1.0

- Added Chinese language.
- Added command-line parameter to force any available user language.
- Code revision with SonarLint.

## 2.1.1

- Rebuild due to a [bug](https://github.com/afpineda/appstrings-python/issues/1) in library "appstrings".
  Thanks to user [Aalexz](https://github.com/Aalexz).No new functionalities.
- Minor changes for [SonarLint](https://docs.sonarsource.com/sonarlint/vs-code/) compliance.
