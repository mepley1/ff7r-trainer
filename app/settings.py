""" Hotkeys and trainer config are defined in this file. """

### GAME VERSION ###
# Set as either 'epic' or 'steam'.
# Memory addresses are defined based on which game version.
# Only tested on Epic version; may or may not work well on Steam version.
GAME_VERSION = 'epic'

### APPEARANCE OPTIONS ###
class Appearance:
    TRANSPARENT_BG = False
    SHOW_IMAGE = True

    # Colors
    BG = '#000813'
    BG_ENTRY = '#273A53'
    FG = '#FFFFFF'
    BLUE = '#53B9FF'
    BLACK = '#000000'
    ACTIVE = '#EB4B98'
    DIM = '#909090'
    ERROR = '#B02020'

    if TRANSPARENT_BG == True:
        # If transparent background set, then use black bg for all buttons/entries
        # to be less distracting when overlaying game window.
        BG_ENTRY = '#000000'

    # Extras / Not currently used
    #BG_LIGHT = '#00193D'
    #GREEN = '#A9ff4E' # Bright green
    #MAGENTA_LIGHT = '#FF66B0' # Lighter magenta

### HOTKEYS ###
# Used by `keyboard` module to set hotkeys, and also displayed on GUI window.
# To edit, use any format readable by `keyboard` module; 
# Strings like below are preferable since these are shown as-is on the trainer.
# but can also use a tuple of scan codes i.e. (29,42,78) for ctrl+shift+plus.
# To find scan codes: run `python -m keyboard` in a terminal, then press keys.
HOTKEYS = {
    # App control
    'HIDE_WINDOW': 'Ctrl + Shift + F12',
    'EXIT': 'Ctrl + Shift + Del',
    'SHOW_TRAINER_INFO': 'Ctrl + Shift + F8',
    'SHOW_PARTY_INFO': 'Ctrl + Shift + F9',

    # Cheat hotkeys
    'CLOUD_GODMODE': 'Ctrl + Num 1',
    'CLOUD_INF_MP': 'Ctrl + Num 2',
    'CLOUD_INF_ATB': 'Ctrl + Num 3',
    'CLOUD_ATK_BOOST': 'Ctrl + Shift + Num /',

    'AERITH_GODMODE': 'Ctrl + Num 4',
    'AERITH_INF_MP': 'Ctrl + Num 5',
    'AERITH_INF_ATB': 'Ctrl + Num 6',

    'ALL_CHARS_GODMODE': 'Ctrl + Shift + Num 1',
    'ALL_CHARS_INF_MP': 'Ctrl + Shift + Num 2',
    'ALL_CHARS_INF_ATB': 'Ctrl + Shift + Num 3',
    'ALL_CHARS_INF_LIMIT': 'Ctrl + Shift + Num 4',

    # For 'add item' widget
    'ADD_ITEM': 'Ctrl + Shift + Plus',
}

### FONTS ###
# Others won't have these fonts installed, so I'm keeping them configurable.
FONTS = {
    'TEXT': 'Play',
    'TITLE': 'Impact',
    'SPECIAL': 'Play',

    'FONT_SIZE': '9',
    'FONT_SIZE_TITLE': '12',
}
