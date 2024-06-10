# FF7 Remake Trainer

A cheat trainer for FF7 Remake Intergrade.

# Usage

Create and activate a venv in root dir, install requirements, then run ./app/gui.py.

On Windows:

`python -m venv venv`

`./venv/Scripts/Activate.ps1`

`pip install -r requirements.txt`

`python ./app/gui.py` (game must be running)

# Config

Configure hotkeys/appearance in `settings.py`.

# Build

On Windows, from project root dir:

1. Configure settings if desired (mainly `TRANSPARENT_BG` and `SHOW_IMAGE`, if you want to change them);
2. Activate venv `./venv/Scripts/Activate.ps1`;
3. Execute `build.bat`.

# Screenshots

Default:

![Demo image](screens/demo.png)

Transparent window: (`TRANSPARENT_BG = True`)

![Demo image](screens/trans.jpg)

Solid window: (`TRANSPARENT_BG = False`)

![Demo image](screens/solid.jpg)
