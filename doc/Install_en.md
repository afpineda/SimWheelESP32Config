# Installing and running

There are some choices as described below.

## Windows bundle

For Windows 64-bits, only.

- Go to the [Releases](https://github.com/afpineda/SimWheelESP32Config/releases) page
  and download the latest file named "**ESP32SimWheel-windows.zip**" (or similar).
- **IMPORTANT note** for Windows 11 users:
  - Right-click on the ZIP file and select *Properties*
  - At the bottom of the properties page, look for a security notice
  - Check the "unblock" box next to it.

  See [this tutorial](https://www.elevenforum.com/t/unblock-file-downloaded-from-internet-in-windows-11.1125/)
  for detailed instructions.

- Unzip to a folder of your choice.

Run the executable in that folder.

## Running from source code

For all platforms with Python support (Windows / Linux / Mac).

To be done only once:

- Python version 3 is required. At the time of writing, this application works fine with **version 3.12.1**.
  If not done yet, download and install [Python](https://www.python.org/downloads/).
- Ensure the python interpreter can be found in your "PATH" environment variable.
  If you have several Python versions installed, ensure the proper one is found first
  in the "PATH" environment variable.
  Alternatively, you may configure a [virtual environment](https://realpython.com/python-virtual-environments-a-primer/)
  ("venv" or "conda") in the installation folder.
- Go to the [Releases](https://github.com/afpineda/SimWheelESP32Config/releases) page
  and download the latest **source code** (in ZIP format).
- Unzip to a folder of your choice.
- Open a shell terminal.
- Place the prompt in the root directory of that folder,
  where the files "LICENSE.md" and "README.md" are found.
- Install library dependencies:

  ```shell
  pip install -r src/requirements.txt
  ```

  or:

  ```shell
  pip install hidapi
  pip install nicegui
  pip install appstrings
  ```

- If something goes wrong, try an older Python version.
- Linux users: follow notes for the Linux bundle above.

In order to run the application, type:

```shell
python <path_to_your_folder>/src/ESP32SimWheelConfig/__main__.py
```

You may want to put that command in a shell script.

## Forcing a specific user language

User language is automatically detected from your operating system environment.
However, you may run the application in a specific user language just by passing
the language code as a command-line argument. For example:

```shell
ESP32SimWheel es
```

or

```shell
python <path_to_your_folder>/src/ESP32SimWheelConfig/__main__.py es
```

Available language codes are:

| Code | Language          |
| ---- | ----------------- |
| en   | English           |
| es   | Spanish (Español) |
| zh   | Chinese (中国)    |
