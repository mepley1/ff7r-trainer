# FF7 Remake Trainer

A cheat trainer for FF7 Remake Intergrade.

# Usage

Create and activate a venv in root dir, install requirements, then run ./app/gui.py.

On Windows:

`python -m venv venv`

`./venv/Scripts/Activate.ps1`

`pip install -r requirements.txt`

`python ./app/gui.py` (or `pythonw` if preferred)

I've also included a pyproject.toml so you can install it as a module if preferred:

`pip install .`

`trainer`

# Config

Configure hotkeys/appearance in `settings.py`.

# Build

Activate venv, then run `./build_all.bat`. It will automate building with Cython, package with pyinstaller and leave an exe in `/dist`.

# Screenshots

Default:

![Demo image](screens/demo.png)

Transparent window: (`TRANSPARENT_BG = True`)

![Demo image](screens/trans.jpg)

Solid window: (`TRANSPARENT_BG = False`)

![Demo image](screens/solid.jpg)
