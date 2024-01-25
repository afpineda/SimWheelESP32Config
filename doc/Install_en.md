# Installing and running

There are some choices as described below.

## Windows bundle

For Windows 64-bits, only.

- Go to the [Releases](https://github.com/afpineda/SimWheelESP32Config/releases) page
  and download the latest file named "**ESP32SimWheel-windows.zip**".
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

In order to run the application, type:

```shell
python <path_to_your_folder>/src/ESP32SimWheelConfig/__main__.py
```

You may want to put that command in a shell script.
