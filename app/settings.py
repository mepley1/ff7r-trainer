""" Hotkeys and trainer config are defined in this file. """

### GAME VERSION ###
# Set as either 'epic' or 'steam'.
# Memory addresses are defined based on which game version.
# Only tested on Epic version; may or may not work well on Steam version.
GAME_VERSION = 'epic'

### APPEARANCE OPTIONS ###
class Appearance:
    ''' General appearance options. '''
    # Transparent background
    TRANSPARENT_BG = False
    # Show cover image on trainer, below the title
    SHOW_IMAGE = True
    HEADER_IMG_PATH = 'assets/ff7r.png'
    # Alpha transparency of entire window. Can be glitchy if set below 1.0
    ALPHA = 1.0
    # Show/hide window manager maximize/minimize controls (win.overrideredirect)
    FRAMELESS_WINDOW = True
    # Enable cheats for individual characters. Otherwise only "all chars" cheats are enabled.
    ENABLE_INDIVIDUAL_CHARS = True

    # Colors
    BG = '#000813'
    BG_ENTRY = '#273A53'
    FG = '#FFFFFF'
    BLUE = '#53B9FF'
    BLACK = '#000000'
    #ACTIVE = '#EB4B98'
    ACTIVE = '#53B9FF'

    DIM = '#909090'
    ERROR = '#B02020'

    if TRANSPARENT_BG == True:
        # If transparent background set, then use black bg for all buttons/entries
        # to be less distracting when overlaying game window.
        BG_ENTRY = '#000000'

    ### FONTS ###
    # Others won't have these fonts installed, so I'm keeping them configurable.
    FONTS = {
        'TEXT': 'Play',
        'TITLE': 'Impact',
        'SPECIAL': 'Play',

        'FONT_SIZE': '9',
        'FONT_SIZE_TITLE': '12',
    }

    # Time to display error messages/highlight labels on cheat usage (seconds).
    FEEDBACK_COOLDOWN = 2

### HOTKEYS ###
# Used by `keyboard` module to set hotkeys, and also displayed on GUI window.
# To edit, use any format readable by `keyboard` module; 
# Strings like below are preferable since these are shown as-is on the trainer.
# but can also use a tuple of scan codes i.e. (29,42,78) for ctrl+shift+plus.
# To find scan codes: run `python -m keyboard` in a terminal, then press keys.
HOTKEYS = {
    # App control
    'EXIT': 'Ctrl + Shift + Del',
    'SHOW_TRAINER_INFO': 'Ctrl + F9',
    'SHOW_PARTY_INFO': 'Ctrl + F10',
    'HIDE_WINDOW': 'Ctrl + F12',

    # Cheat hotkeys
    'CLOUD_GODMODE': 'Ctrl + Shift + Num 1',
    'CLOUD_INF_MP': 'Ctrl + Shift + Num 2',
    'CLOUD_INF_ATB': 'Ctrl + Shift + Num 3',
    'CLOUD_ATK_BOOST': 'Ctrl + Shift + /',

    'AERITH_GODMODE': 'Ctrl + Shift + Num 4',
    'AERITH_INF_MP': 'Ctrl + Shift + Num 5',
    'AERITH_INF_ATB': 'Ctrl + Shift + Num 6',

    'ALL_CHARS_GODMODE': 'Ctrl + Num 1',
    'ALL_CHARS_INF_MP': 'Ctrl + Num 2',
    'ALL_CHARS_INF_ATB': 'Ctrl + Num 3',
    'ALL_CHARS_INF_LIMIT': 'Ctrl + Num 4',
    'ALL_CHARS_ATK_BOOST': 'Ctrl + Num 5',
    'ALL_CHARS_LUCK_BOOST': 'Ctrl + Num 6',

    'HARDMODE_AP_MULTIPLIER': 'Ctrl + Num 8',
    'HARDMODE_EXP_MULTIPLIER': 'Ctrl + Num 9',

    # For 'add item' widget
    'ADD_ITEM': 'Ctrl + Plus',
}

### DEBUGGING/DEVELOPMENT ###
# Don't create process handle before initializing GUI (bool):
# If True, enables to load GUI without game running; though any actions will result in exceptions.
SKIP_CREATING_PROCESS_HANDLE = False
# Log to either stdout or a file. ('file' or 'stdout')
# If running Cython build, app will log to the file regardless of LOG_TARGET setting.
LOG_TARGET = 'file'
LOG_FILE = 'log.log'


### MISC ###
intro_msg: str = '''
 ███████████ ███████████ ██████████                                  
░░███░░░░░░█░░███░░░░░░█░███░░░░███                                  
 ░███   █ ░  ░███   █ ░ ░░░    ███                                   
 ░███████    ░███████         ███                                    
 ░███░░░█    ░███░░░█        ███                                     
 ░███  ░     ░███  ░        ███                                      
 █████       █████         ███                                       
░░░░░       ░░░░░         ░░░                                        
 ███████████                                      █████              
░░███░░░░░███                                    ░░███               
 ░███    ░███   ██████  █████████████    ██████   ░███ █████  ██████ 
 ░██████████   ███░░███░░███░░███░░███  ░░░░░███  ░███░░███  ███░░███
 ░███░░░░░███ ░███████  ░███ ░███ ░███   ███████  ░██████░  ░███████ 
 ░███    ░███ ░███░░░   ░███ ░███ ░███  ███░░███  ░███░░███ ░███░░░  
 █████   █████░░██████  █████░███ █████░░████████ ████ █████░░██████ 
░░░░░   ░░░░░  ░░░░░░  ░░░░░ ░░░ ░░░░░  ░░░░░░░░ ░░░░ ░░░░░  ░░░░░░  
 ███████████                      ███                                
░█░░░███░░░█                     ░░░                                 
░   ░███  ░  ████████   ██████   ████  ████████    ██████  ████████  
    ░███    ░░███░░███ ░░░░░███ ░░███ ░░███░░███  ███░░███░░███░░███ 
    ░███     ░███ ░░░   ███████  ░███  ░███ ░███ ░███████  ░███ ░░░  
    ░███     ░███      ███░░███  ░███  ░███ ░███ ░███░░░   ░███      
    █████    █████    ░░████████ █████ ████ █████░░██████  █████     
   ░░░░░    ░░░░░      ░░░░░░░░ ░░░░░ ░░░░ ░░░░░  ░░░░░░  ░░░░░      
                        - by RogueAutomata -
                   - 100% organic LLM-free code -
                        - code@mepley.net -
'''
