# pymem docs: https://pymem.readthedocs.io/en/stable/api_pymem_memory.html
# int = 4 bytes
# uint = unsigned int
# short = 2 bytes
# ushort = unsigned short
# float = float 4 bytes

# game notes:
# player: ff7remake_.exe+579D6E8
# data: ff7remake_.exe+57F75B8

import keyboard # for hotkeys
from pymem import *
from pymem.process import *
from tkinter import *
#from tkinter.ttk import *
from threading import Thread
from time import sleep
from typing import List

from settings import * # settings.py

print('\n Looking for ff7remake_.exe ...')
try:
    mem = Pymem('ff7remake_.exe')
except:
    print('Game not running! Couldnt find ff7remake_.exe')
    quit()
game_module = module_from_name(mem.process_handle, 'ff7remake_.exe').lpBaseOfDll

### Pointers

# Bases
player_base = game_module + 0x579D6E8
data_base = game_module + 0x57F75B8
base_3 = game_module + 0x0579DAE8 # This is used in one of the tables I've got

# These are offset from player_base
cloud_hp_offsets = [0xB6D80, 0x3E60, 0x30] # ushort
cloud_max_hp_offsets = [0xB6D80, 0x3E60, 0x34] # ushort
cloud_mp_offsets = [0xB6D80, 0x3E60, 0x38] # 1 byte
cloud_max_mp_offsets = [0xB6D80, 0x3E60, 0x3C] # 1 byte
cloud_atb_offsets = [0xB6D80, 0x3E60, 0x44] # float (1000 per bar)
cloud_atk_offsets = [0xB6D80, 0x3E60, 0x48] # 1 byte
cloud_magic_atk_offsets = [0xB6D80, 0x3E60, 0x4C] # 1 byte

# Offsets from base_3
# All these seem to be fine as uint, unless otherwise noted.
aerith_hp_offsets = [0x8, 0x8, 0xF0]
aerith_max_hp_offsets = [0x8, 0x8, 0xF4]
aerith_mp_offsets = [0x8, 0x8, 0xF8]
aerith_max_mp_offsets = [0x8, 0x8, 0xFC]
aerith_atb_offsets = [0x8, 0x8, 0x104] #float
aerith_luck_offsets = [0x8, 0x8, 0x118]

tifa_hp_offsets = [0x8, 0x8, 0xB0]
tifa_max_hp_offsets = [0x8, 0x8, 0xB4]
tifa_mp_offsets = [0x8, 0x8, 0xB8]
tifa_max_mp_offsets = [0x8, 0x8, 0xBC]
tifa_atb_offsets = [0x8, 0x8, 0xC4] #float
tifa_luck_offsets = [0x8, 0x8, 0xD8]

barret_hp_offsets = [0x8, 0x8, 0x70]
barret_max_hp_offsets = [0x8, 0x8, 0x74]
barret_mp_offsets = [0x8, 0x8, 0x78]
barret_max_mp_offsets = [0x8, 0x8, 0x7C]
barret_atb_offsets = [0x8, 0x8, 0x84] #float
barret_luck_offsets = [0x8, 0x8, 0x98]

cloud_luck_offsets = [0x8, 0x8, 0x58]

'''
# Already have these as offsets from player_base, but here's the same ones offset from base_3
cloud_hp_offsets = [0x8, 0x8, 0x30] # ushort
cloud_max_hp_offsets = [0x8, 0x8, 0x34]
cloud_mp_offsets = [0x8, 0x8, 0x38] # 1 byte
cloud_max_mp_offsets = [0x8, 0x8, 0x3C] # 1 byte
cloud_atb_offsets = [0x8, 0x8, 0x44] # float (1000 per bar)
cloud_luck_offsets = [0x8, 0x8, 0x58]
'''

# Inventory items, offset from player_base
ether_offsets = [0x3567C] #player, uint
adrenaline_offsets = [0x35814] #player, uint
gil_offsets = [0x356C4] #player, uint
moogle_medals_offsets = [0x3570C] #player, uint

# These are offset from data_base
player_atb_rate_offsets = [0x38, 0x719C] #data, float (normal = 1)
ai_atb_rate_offsets = [0x38, 0x751C] #data, float (normal = 0.349999994)


### Helper functions

# Get pointer address
def getPtrAddr(address: int, offsets: List[int]):
    addr = mem.read_int(address)
    for offset in offsets:
        if offset != offsets[-1]:
            addr = mem.read_int(addr + offset)
    addr = addr + offsets[-1]
    return addr

# Read a value (uint)
def read_uint(base, offsets: List[int]):
    value = mem.read_uint(getPtrAddr(base, offsets))
    return value

# Highlight cheat label for a few seconds. (starts a thread to avoid blocking)
def temp_highlight(labels: list):

    def highlight():
        for label in labels:
            label.config(fg=ACTIVE)
        sleep(2)
        for label in labels:
            label.config(fg=FG)
        
    hl_thread = Thread(target = highlight).start()

# Update cheat label's text color, for togglable cheats
def update_label_color(color: StringVar, *labels):
    for label in labels:
        label.config(fg=color)

### CHEATS

# Inventory

# Get moogle medals
def read_moogle_medals():
    moogle_medals = mem.read_uint(getPtrAddr(player_base, moogle_medals_offsets))
    return moogle_medals

print('moogle medals: ', read_moogle_medals()) # Read+print for testing

# Gil
def add_gil(num_gil: int):
    current_gil = mem.read_uint(getPtrAddr(player_base, gil_offsets))
    mem.write_uint(getPtrAddr(player_base, gil_offsets), current_gil + num_gil)
    # Highlight the GUI label
    temp_highlight([modmenu.add_gil_label, modmenu.add_gil_effect_label])
    print(f'Added {num_gil} gil.')

### Cloud ###

# get HP (cloud)
def get_current_hp():
    current_hp = mem.read_ushort(getPtrAddr(player_base, cloud_hp_offsets))
    print('current hp (Cloud): ', current_hp)

get_current_hp()

# Get Cloud's max HP, and heal fully
def heal_cloud():
    cloud_max_hp = mem.read_ushort(getPtrAddr(player_base, cloud_max_hp_offsets))
    mem.write_ushort(getPtrAddr(player_base, cloud_hp_offsets), cloud_max_hp)
    print('Healed Cloud. ')

# Same, for MP
def cloud_mp_refill():
    cloud_max_mp = mem.read_ushort(getPtrAddr(player_base, cloud_max_mp_offsets))
    mem.write_ushort(getPtrAddr(player_base, cloud_mp_offsets), cloud_max_mp)
    print('max MP: ', cloud_max_mp, '. Refilled')

# Cloud ATB
def cloud_atb_refill():
    cloud_current_atb = mem.read_float(getPtrAddr(player_base, cloud_atb_offsets))
    if cloud_current_atb < 2000.0:
        mem.write_float(getPtrAddr(player_base, cloud_atb_offsets), 2000.0)
    print('Cloud ATB filled')

# Player ATB rate - set rate to desired_rate. Normal = 1
def set_player_atb_rate(desired_rate: float):
    mem.write_float(getPtrAddr(data_base, player_atb_rate_offsets), desired_rate)

def cloud_atk_boost():
    #cloud_atk = mem.read_ushort(getPtrAddr(player_base, cloud_atk_offsets))
    mem.write_ushort(getPtrAddr(player_base, cloud_atk_offsets), 3000) #physical atk
    mem.write_ushort(getPtrAddr(player_base, cloud_magic_atk_offsets), 3000) #physical atk
    #print('Boosted Cloud\s ATK (until game re-calculates)')

### Aerith ###

# Get Aerith max HP, and heal fully
def aerith_heal():
    aerith_max_hp = mem.read_uint(getPtrAddr(base_3, aerith_max_hp_offsets))
    mem.write_uint(getPtrAddr(base_3, aerith_hp_offsets), aerith_max_hp)
    print('Healed Aerith.')

# Aerith MP
def aerith_mp_refill():
    aerith_max_mp = mem.read_ushort(getPtrAddr(base_3, aerith_max_mp_offsets))
    mem.write_ushort(getPtrAddr(base_3, aerith_mp_offsets), aerith_max_mp)
    print('Aerith max MP: ', aerith_max_mp, '. Refilled')

# aerith ATB
def aerith_atb_refill():
    aerith_current_atb = mem.read_float(getPtrAddr(base_3, aerith_atb_offsets))
    if aerith_current_atb < 2000.0:
        mem.write_float(getPtrAddr(base_3, aerith_atb_offsets), 2000.0)
    print('Aerith ATB filled')

### Barret ###

# Heal
def barret_heal():
    barret_max_hp = mem.read_uint(getPtrAddr(base_3, barret_max_hp_offsets))
    mem.write_uint(getPtrAddr(base_3, barret_hp_offsets), barret_max_hp)
    print('Barret healed')

def barret_mp_refill():
    barret_max_mp = mem.read_ushort(getPtrAddr(base_3, barret_max_mp_offsets))
    mem.write_ushort(getPtrAddr(base_3, barret_mp_offsets), barret_max_mp)
    print('Barret max MP: ', barret_max_mp, '. Refilled')

def barret_atb_refill():
    barret_current_atb = mem.read_float(getPtrAddr(base_3, barret_atb_offsets))
    if barret_current_atb < 2000.0:
        mem.write_float(getPtrAddr(base_3, barret_atb_offsets), 2000.0)
    print('Barret ATB filled')

### Tifa ###

# Heal
def tifa_heal():
    tifa_max_hp = mem.read_uint(getPtrAddr(base_3, tifa_max_hp_offsets))
    mem.write_uint(getPtrAddr(base_3, tifa_hp_offsets), tifa_max_hp)
    print('Tifa healed')

def tifa_mp_refill():
    tifa_max_mp = mem.read_ushort(getPtrAddr(base_3, tifa_max_mp_offsets))
    mem.write_ushort(getPtrAddr(base_3, tifa_mp_offsets), tifa_max_mp)
    print('Tifa max MP: ', tifa_max_mp, '. Refilled')

def tifa_atb_refill():
    tifa_current_atb = mem.read_float(getPtrAddr(base_3, tifa_atb_offsets))
    if tifa_current_atb < 2000.0:
        mem.write_float(getPtrAddr(base_3, tifa_atb_offsets), 2000.0)
    print('Tifa ATB filled')


# Infinite x cheats (toggle functions):

godmode_on = False
inf_mp_on = False
inf_atb_on = False
cloud_atk_boost_on = False

aerith_godmode_on = False
aerith_inf_mp_on = False
aerith_inf_atb_on = False

all_chars_godmode_on = False # Godmode for all characters
all_chars_inf_mp_on = False # Inf MP for all
all_chars_inf_atb_on = False # Inf ATB for all chars

# Cloud
def cloud_godmode_toggle():
    # Toggle godmode on/off
    global godmode_on
    if godmode_on == True:
        # If on, turn it off
        godmode_on = False
        #print('godmode turned OFF (Cloud)')
        update_label_color(FG, modmenu.godmode_label, modmenu.godmode_effect_label)
    else:
        # If off, turn it on
        godmode_on = True
        #print('godmode turned ON (Cloud)')
        update_label_color(ACTIVE, modmenu.godmode_label, modmenu.godmode_effect_label)

def cloud_inf_mp_toggle():
    # Toggle inf mp on/off cloud
    global inf_mp_on
    if inf_mp_on == True:
        # If on, turn it off
        inf_mp_on = False
        print('inf MP turned OFF')
        update_label_color(FG, modmenu.mp_label, modmenu.mp_effect_label)
    else:
        # If off, turn it on
        inf_mp_on = True
        print('inf MP turned ON')
        update_label_color(ACTIVE, modmenu.mp_label, modmenu.mp_effect_label)

def inf_atb_toggle():
    #Toggle inf ATB on/off cloud
    global inf_atb_on
    if inf_atb_on == True:
        inf_atb_on = False
        print('Inf ATB OFF')
        update_label_color(FG, modmenu.cloud_atb_label, modmenu.atb_effect_label)
    else:
        inf_atb_on = True
        print('Inf ATB ON')
        update_label_color(ACTIVE, modmenu.cloud_atb_label, modmenu.atb_effect_label)

def cloud_atk_boost_toggle():
    #Toggle atk boost on/off cloud
    global cloud_atk_boost_on
    if cloud_atk_boost_on == True:
        cloud_atk_boost_on = False
        print('Cloud ATK boost OFF')
        update_label_color(FG, modmenu.cloud_atk_boost_label, modmenu.cloud_atk_boost_effect_label)
    else:
        cloud_atk_boost_on = True
        print('cloud_atk_boost ON')
        update_label_color(ACTIVE, modmenu.cloud_atk_boost_label, modmenu.cloud_atk_boost_effect_label)

# Aerith

def aerith_godmode_toggle():
    # Toggle godmode on/off
    global aerith_godmode_on
    if aerith_godmode_on == True:
        # If on, turn it off
        aerith_godmode_on = False
        print('godmode turned OFF (Aerith)')
        update_label_color(FG, modmenu.aerith_godmode_label, modmenu.aerith_godmode_effect_label)
    else:
        # If off, turn it on
        aerith_godmode_on = True
        print('godmode turned ON (Aerith)')
        update_label_color(ACTIVE, modmenu.aerith_godmode_label, modmenu.aerith_godmode_effect_label)

def aerith_inf_mp_toggle():
    # Toggle inf mp on/off
    global aerith_inf_mp_on
    if aerith_inf_mp_on == True:
        # If on, turn it off
        aerith_inf_mp_on = False
        print('Inf MP turned OFF (Aerith)')
        update_label_color(FG, modmenu.aerith_inf_mp_label, modmenu.aerith_inf_mp_effect_label)
    else:
        # If off, turn it on
        aerith_inf_mp_on = True
        print('Inf MP turned ON (aerith)')
        update_label_color(ACTIVE, modmenu.aerith_inf_mp_label, modmenu.aerith_inf_mp_effect_label)

def aerith_inf_atb_toggle():
    #Toggle inf ATB on/off
    global aerith_inf_atb_on
    if aerith_inf_atb_on == True:
        aerith_inf_atb_on = False
        print('Inf ATB OFF (aerith)')
        update_label_color(FG, modmenu.aerith_inf_atb_label, modmenu.aerith_inf_atb_effect_label)
    else:
        aerith_inf_atb_on = True
        print('Inf ATB ON (aerith)')
        update_label_color(ACTIVE, modmenu.aerith_inf_atb_label, modmenu.aerith_inf_atb_effect_label)

# All characters

def all_chars_godmode_toggle():
    global all_chars_godmode_on
    if all_chars_godmode_on == True:
        all_chars_godmode_on = False
        print('Godmode turned OFF (all chars)')
        modmenu.all_chars_godmode_effect_label.config(foreground=FG)
        modmenu.all_chars_godmode_label.config(foreground=FG)
    else:
        all_chars_godmode_on = True
        print('Godmode turned ON (all chars)')
        #modmenu.change_label_color(modmenu.all_chars_godmode_effect_label, ACTIVE)
        modmenu.all_chars_godmode_effect_label.config(foreground=ACTIVE)
        modmenu.all_chars_godmode_label.config(foreground=ACTIVE)

def all_chars_inf_mp_toggle():
    # Toggle inf mp on/off
    global all_chars_inf_mp_on
    if all_chars_inf_mp_on == True:
        # If on, turn it off
        all_chars_inf_mp_on = False
        print('Inf MP turned OFF (all chars)')
        update_label_color(FG, modmenu.all_chars_inf_mp_label, modmenu.all_chars_inf_mp_effect_label)
    else:
        # If off, turn it on
        all_chars_inf_mp_on = True
        print('Inf MP turned ON (all chars)')
        update_label_color(ACTIVE, modmenu.all_chars_inf_mp_label, modmenu.all_chars_inf_mp_effect_label)

def all_chars_inf_atb_toggle():
    global all_chars_inf_atb_on
    if all_chars_inf_atb_on == True:
        all_chars_inf_atb_on = False
        print('Inf ATB turned OFF (all chars)')
        update_label_color(FG, modmenu.all_chars_inf_atb_label, modmenu.all_chars_inf_atb_effect_label)
    else:
        all_chars_inf_atb_on = True
        print('inf_atb turned ON (all chars)')
        update_label_color(ACTIVE, modmenu.all_chars_inf_atb_label, modmenu.all_chars_inf_atb_effect_label)

### GUI

class ModMenu():
    def __init__(self, window_title, width, height):

        self.win = Tk()
        #x, y = self.center(width, height)
        #self.win.geometry(f"{width}x{height}+{x}+{y}")
        self.win.overrideredirect(True)
        self.win.wm_attributes("-topmost", 1)
        self.win.wm_attributes("-alpha", 0.8)
        self.win.configure(background=BG)

        # Add some default widget options, to reduce repeating styles. Use values from settings.py
        self.win.option_add("*Font", (FONTNAME, FONT_SIZE))

        self.win.option_add("*Label*Background", BG)
        self.win.option_add("*Label*Foreground", FG)
        self.win.option_add("*Label*Font", (FONTNAME, FONT_SIZE))

        self.win.option_add("*Button*Background", BG)
        self.win.option_add("*Button*Foreground", FG)
        self.win.option_add("*Button*Font", (FONTNAME, FONT_SIZE))
        self.win.option_add("*Button*BorderWidth", 1)
        self.win.option_add("*Button*Relief", 'solid')


        ## Title label

        self.title_label = Label(self.win, text=window_title, font=(FONTNAME_SPECIAL, FONT_SIZE_TITLE), foreground=BLUE)
        self.title_label.grid(column=0, row=0, sticky='news', padx=48, columnspan=2)

        self.author_label = Label(self.win, text='By rogueautomata')
        self.author_label.grid(column=0, row=1, sticky='news', padx=48, columnspan=2)

        # Image 
        self.image = PhotoImage(file="FFVIIRemake.png")
        self.image_label = Label(image=self.image, background=BG, height=128)
        self.image_label.grid(column=0, row=2, sticky='news', columnspan=2)


        ## Info labels

        self.hotkeys_label = Label(self.win, text='Hotkey', font=(FONTNAME_SPECIAL, FONT_SIZE_TITLE), foreground=BLUE)
        self.effect_label = Label(self.win, text='Effect', font=(FONTNAME_SPECIAL, FONT_SIZE_TITLE), foreground=BLUE)

        self.hotkeys_label.grid(column=0, row=5, sticky='wns', pady=(0,16))
        self.effect_label.grid(column=1, row=5, sticky='wns', pady=(0,16))

        ## Hotkeys labels ##

        # Cloud Godmode
        #self.godmode_label = Label(self.win, text="Ctrl + Num 1")
        self.godmode_label = Label(self.win, text=HOTKEY_CLOUD_GODMODE)
        self.godmode_label.grid(column=0, row=12, sticky='wns')

        #self.cloud_godmode_btn = Button(self.win, text="Godmode Cloud", font=(FONTNAME,FONT_SIZE), background=BG, foreground=FG, command=cloud_godmode_toggle)
        #self.cloud_godmode_btn.grid(column=1,row=12,sticky='wens')

        self.godmode_effect_label = Label(self.win, text="Cloud Godmode")
        self.godmode_effect_label.grid(column=1, row=12, sticky='wns')

        '''# Cloud HP heal label + button
        self.cloud_heal_label = Label(self.win, text="Ctrl + num 8")
        self.cloud_heal_label.grid(column=0, row=13, sticky='wns')

        self.heal_effect_label = Label(self.win, text="Cloud Heal")
        self.heal_effect_label.grid(column=1, row=13, sticky='wns')'''

        ## Cloud Inf MP button
        self.mp_label = Label(self.win, text=HOTKEY_CLOUD_INF_MP)
        self.mp_label.grid(column=0, row=14, sticky='wns')

        self.mp_effect_label = Button(self.win, text="Cloud Inf MP", command=cloud_inf_mp_toggle)
        self.mp_effect_label.grid(column=1,row=14,sticky='wns')
        #self.mp_effect_label = Label(self.win, text="Cloud Inf MP")
        #self.mp_effect_label.grid(column=1, row=14, sticky='wns')

        '''
        ## Cloud MP Refill
        self.mp_refill_label = Label(self.win, text="Num 3")
        self.mp_refill_label.grid(column=0, row=15, sticky='wns')

        self.mp_refill_effect_label = Label(self.win, text="Refill MP Cloud")
        self.mp_refill_effect_label.grid(column=1, row=15, sticky='wns')'''

        # Cloud Inf ATB
        self.cloud_atb_label = Label(self.win, text=HOTKEY_CLOUD_INF_ATB)
        self.cloud_atb_label.grid(column=0, row=16, sticky='wns')

        self.atb_effect_label = Label(self.win, text="Cloud Inf ATB")
        self.atb_effect_label.grid(column=1, row=16, sticky='wns')

        # Cloud Attack boost
        self.cloud_atk_boost_label = Label(self.win, text=HOTKEY_CLOUD_ATK_BOOST)
        self.cloud_atk_boost_label.grid(column=0, row=17, sticky='wns')

        self.cloud_atk_boost_effect_label = Label(self.win, text="Cloud Attack Boost")
        self.cloud_atk_boost_effect_label.grid(column=1, row=17, sticky='wns')

        # Spacer
        self.spacer = Label(self.win).grid(column=0, row=18, columnspan=2)

        ### Aerith labels
        self.aerith_godmode_label = Label(self.win, text=HOTKEY_AERITH_GODMODE)
        self.aerith_godmode_label.grid(column=0, row=20, sticky='wns')

        self.aerith_godmode_effect_label = Label(self.win, text="Aerith Godmode")
        self.aerith_godmode_effect_label.grid(column=1, row=20, sticky='wns')

        self.aerith_inf_mp_label = Label(self.win, text=HOTKEY_AERITH_INF_MP)
        self.aerith_inf_mp_label.grid(column=0, row=22, sticky='wns')

        self.aerith_inf_mp_effect_label = Label(self.win, text="Aerith Inf MP")
        self.aerith_inf_mp_effect_label.grid(column=1, row=22, sticky='wns')

        self.aerith_inf_atb_label = Label(self.win, text=HOTKEY_AERITH_INF_ATB)
        self.aerith_inf_atb_label.grid(column=0, row=23, sticky='wns')

        self.aerith_inf_atb_effect_label = Label(self.win, text="Aerith Inf ATB")
        self.aerith_inf_atb_effect_label.grid(column=1, row=23, sticky='wns')

        ### All-characters cheats
        # godmode all
        self.all_chars_godmode_label = Label(self.win, text=HOTKEY_ALL_CHARS_GODMODE)
        self.all_chars_godmode_label.grid(column=0, row=90, sticky='wns', pady=(16,0))

        self.all_chars_godmode_effect_label = Label(self.win, text="All Godmode")
        self.all_chars_godmode_effect_label.grid(column=1, row=90, sticky='wns', pady=(16,0))

        # Inf MP all
        self.all_chars_inf_mp_label = Label(self.win, text=HOTKEY_ALL_CHARS_INF_MP)
        self.all_chars_inf_mp_label.grid(column=0, row=91, sticky='wns')

        self.all_chars_inf_mp_effect_label = Label(self.win, text="All Inf MP")
        self.all_chars_inf_mp_effect_label.grid(column=1, row=91, sticky='wns')

        # Inf ATB all
        self.all_chars_inf_atb_label = Label(self.win, text=HOTKEY_ALL_CHARS_INF_ATB)
        self.all_chars_inf_atb_label.grid(column=0, row=92, sticky='wns')

        self.all_chars_inf_atb_effect_label = Label(self.win, text="All Inf ATB")
        self.all_chars_inf_atb_effect_label.grid(column=1, row=92, sticky='wns')

        ### Inventory
        self.add_gil_label = Label(self.win, text=HOTKEY_ADD_GIL)
        self.add_gil_label.grid(column=0, row=98, sticky='wns', pady=(16,0))

        self.add_gil_effect_label = Label(self.win, text="+5000 Gil")
        self.add_gil_effect_label.grid(column=1, row=98, sticky='wns', pady=(16,0))


        # Toggle window display
        self.open_label = Label(self.win, text=HOTKEY_OPEN, foreground=DIM)
        self.open_label.grid(column=0, row=99, sticky='wns', pady=(16,0))

        self.open_effect_label = Label(self.win, text="Show/hide window", foreground=DIM)
        self.open_effect_label.grid(column=1, row=99, sticky='wns', pady=(16,0))

        # Exit button
        #self.exit_btn = Button(self.win, text="Exit", font=(FONTNAME,FONT_SIZE), background=BG, foreground=FG, relief='solid', borderwidth=1, command=self.win.destroy)
        self.exit_btn = Button(self.win, text="Exit", command=self.win.destroy)
        self.exit_btn.grid(column=0, row=100, sticky='wens', columnspan=2, pady=(16,0))
        print(self.exit_btn.keys())


    def center(self, width, height):
        swidth = self.win.winfo_screenwidth()
        sheight = self.win.winfo_screenheight()
        x = (swidth/2) - (width/2)
        y = (sheight/2) - (height/2)
        return int(x), int(y)

    # Change color of label text, to hint active/inactive
    def change_label_color(self, label, color):
        label.config(foreground=color)

# Change a label's color
def change_text_color(label, color):
    label.config(foreground=color)

# Set hotkeys - works, but a lil janky?

#keyboard.add_hotkey('ctrl + num 8', heal_cloud)
#keyboard.add_hotkey(HOTKEY_CLOUD_MP, cloud_mp_refill)

keyboard.add_hotkey(HOTKEY_CLOUD_GODMODE, cloud_godmode_toggle)
keyboard.add_hotkey(HOTKEY_CLOUD_INF_MP, cloud_inf_mp_toggle)
keyboard.add_hotkey(HOTKEY_CLOUD_INF_ATB, inf_atb_toggle)
keyboard.add_hotkey('ctrl + shift + -', cloud_atk_boost_toggle)

keyboard.add_hotkey(HOTKEY_AERITH_GODMODE, aerith_godmode_toggle)
keyboard.add_hotkey(HOTKEY_AERITH_INF_MP, aerith_inf_mp_toggle)
keyboard.add_hotkey(HOTKEY_AERITH_INF_ATB, aerith_inf_atb_toggle)

keyboard.add_hotkey(HOTKEY_ALL_CHARS_GODMODE, all_chars_godmode_toggle)
keyboard.add_hotkey(HOTKEY_ALL_CHARS_INF_MP, all_chars_inf_mp_toggle)
keyboard.add_hotkey(HOTKEY_ALL_CHARS_INF_ATB, all_chars_inf_atb_toggle)

keyboard.add_hotkey(HOTKEY_ADD_GIL, add_gil, args=(5000,))

#print('press ctrl+shift+f8 to heal cloud...')
#keyboard.wait('ctrl+shift+f8') #blocks like while true

def keybinds(modmenu):
    isopen = True
    while True:
        if keyboard.is_pressed(HOTKEY_OPEN):
            if isopen == True:
                modmenu.win.withdraw()
                isopen = False
            else:
                modmenu.win.deiconify()
                isopen = True
                modmenu.win.focus_force()
            sleep(0.5)

# Godmode cheat - check if godmode is turned on, if so then heal
def keybinds_godmode():
    while True:
        if godmode_on == True:
            heal_cloud()
        else:
            pass
        sleep(2)

# Cloud inf MP daemon
def keybinds_inf_mp_cloud():
    while True:
        if inf_mp_on == True:
            cloud_mp_refill()
        else:
            pass
        sleep(5)

# Inf ATB daemon
def keybinds_inf_atb():
    while True:
        if inf_atb_on == True:
            #set_player_atb_rate(10.0)
            cloud_atb_refill()
        else:
            #set_player_atb_rate(1.0)
            pass
        sleep(4)

# Cloud Attack boost daemon
def keybinds_cloud_atk_boost():
    while True:
        if cloud_atk_boost_on == True:
            cloud_atk_boost()
        else:
            pass
        sleep(1)

# Aerith daemons
def keybinds_aerith_godmode():
    while True:
        if aerith_godmode_on == True:
            aerith_heal()
        else:
            pass
        sleep(2)
def keybinds_aerith_inf_mp():
    while True:
        if aerith_inf_mp_on == True:
            aerith_mp_refill()
        else:
            pass
        sleep(5)
def keybinds_aerith_inf_atb():
    while True:
        if aerith_inf_atb_on == True:
            aerith_atb_refill()
        else:
            pass
        sleep(4)

# All-characters daemons
def keybinds_all_chars_godmode():
    while True:
        if all_chars_godmode_on == True:
            heal_cloud()
            tifa_heal()
            barret_heal()
            aerith_heal()
        else:
            pass
        sleep(2)

def keybinds_all_chars_inf_mp():
    while True:
        if all_chars_inf_mp_on == True:
            cloud_mp_refill()
            tifa_mp_refill()
            barret_mp_refill()
            aerith_mp_refill()
        else:
            pass
        sleep(5)

def keybinds_all_chars_inf_atb():
    while True:
        if all_chars_inf_atb_on == True:
            cloud_atb_refill()
            tifa_atb_refill()
            barret_atb_refill()
            aerith_atb_refill()
        else:
            pass
        sleep(4)


modmenu = ModMenu("FF7 Remake Trainer", 350, 200)

# Open window keybind thread
keybinds_thread = Thread(target = keybinds, args=(modmenu,), daemon = True)
keybinds_thread.start()

### Cloud threads ###
# cloud Godmode thread
cloud_godmode_thread = Thread(target = keybinds_godmode, daemon = True)
cloud_godmode_thread.start()

# Cloud Inf MP thread
cloud_inf_mp_thread = Thread(target = keybinds_inf_mp_cloud, daemon = True)
cloud_inf_mp_thread.start()

# Cloud Inf ATB thread
cloud_inf_atb_thread = Thread(target = keybinds_inf_atb, daemon = True)
cloud_inf_atb_thread.start()

# Cloud Atk boost thread
cloud_atk_boost_thread = Thread(target = keybinds_cloud_atk_boost, daemon = True)
cloud_atk_boost_thread.start()

### Aerith threads ###
# Godmode thread
aerith_godmode_thread = Thread(target = keybinds_aerith_godmode, daemon = True)
aerith_godmode_thread.start()

# Inf MP thread
aerith_inf_mp_thread = Thread(target = keybinds_aerith_inf_mp, daemon = True)
aerith_inf_mp_thread.start()

# Inf ATB thread
aerith_inf_atb_thread = Thread(target = keybinds_aerith_inf_atb, daemon = True)
aerith_inf_atb_thread.start()

### All-chars threads ###
# godmode
all_chars_godmode_thread = Thread(target = keybinds_all_chars_godmode, daemon = True)
all_chars_godmode_thread.start()
# inf mp
all_chars_inf_mp_thread = Thread(target = keybinds_all_chars_inf_mp, daemon = True)
all_chars_inf_mp_thread.start()
# inf atb
all_chars_inf_atb_thread = Thread(target = keybinds_all_chars_inf_atb, daemon = True)
all_chars_inf_atb_thread.start()



modmenu.win.mainloop()
