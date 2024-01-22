# Notes and commentaries for software developers

## Fundamentals

This app interfaces hardware devices through HID feature reports.
The binary format of those reports is called "data version", which is reported by the device itself.
See [HID notes](https://github.com/afpineda/OpenSourceSimWheelESP32/blob/main/doc/firmware/HID_notes.md)
for a complete description.

The source code includes a "module" which can be reused for custom applications.
Implements all the details to enumerate and interface supported devices.

## Source code

In fact, there are two different implementations for this app,
as described bellow.

### Python implementation

Currently active and maintained.

It was tested successfully with Python 3.12, however, PyInstaller does not work with that version.
Use Python 3.11.7 for freezing.

Direct release dependencies are:

- [hidapi](https://pypi.org/project/hidapi/)
- [NiceGUI](https://pypi.org/project/nicegui/)

There is a "requirements.txt" file for all dependencies.

Development dependencies includes [PyInstaller](https://pypi.org/project/pyinstaller/).

At the time of writing, it was not possible to freeze using "zipapp" with success.

### Delphi implementation

Can be found in the "delphi-implementation" branch of this project. Currently not active but maintained.
However, this situation could be reverted in the future.
This implementation works with data version 1.1, but not with previous ones.

## Future work

**The decision to continue development with one technology or another
depends on the drawbacks of those technologies and may
change in the future.**
