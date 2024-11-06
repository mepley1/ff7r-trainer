""" Main app module, contains GUI and logic. """

import contextlib #For ap multiplier context manager
import cython
import functools
import keyboard
import logging, sys
from datetime import datetime, timedelta #for timed_cache wrapper
from pymem import *
from pymem.process import *
from pymem.ptypes import RemotePointer
from tkinter import *
from tkinter import messagebox
from threading import Thread, Event
from time import sleep
from typing import List

import settings #settings.py - App settings
from offsets import Offsets #offsets.py - All offsets

# Import pyinstaller splash module if app was bundled with pyinstaller
# Ref: https://pyinstaller.org/en/stable/runtime-information.html
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    import pyi_splash

# Functions to control splash screen added by pyinstaller
def update_splash(spl_txt: str = '') -> None:
    '''Update splash screen text, if running pyi bundle.'''
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        pyi_splash.update_text(spl_txt)

def kill_splash() -> None:
    '''Kill pyinstaller splash screen.'''
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        pyi_splash.close()

# Configure logging
if settings.LOG_TARGET == 'stdout':
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
else:
    # If running via pythonw.exe then I'll want logs in a file.
    # Write mode rather than default append, to keep only logs from last run.
    logging.basicConfig(level=logging.DEBUG, filename=settings.LOG_FILE, filemode='w')

# Print intro to stdout, don't spam logs with it.
#print(settings.intro_msg)

logging.debug(f'Launch time: {datetime.now()}')

# Note:
if cython.compiled:
    logging.debug('Running Cython build.')

# Attach to exe
if not settings.SKIP_CREATING_PROCESS_HANDLE:
 
    logging.debug('Attempting to attach to ff7remake_.exe ...')
    update_splash('Getting process handle ...')

    try:
        mem = Pymem('ff7remake_.exe')
    except pymem.exception.ProcessNotFound:
        _not_found_msg: str = 'Couldn\'t find ff7remake_.exe. Launch game and try again.'
        logging.error(_not_found_msg)
        # Close pyinstaller splash screen if present
        kill_splash()
        # Display error message in a tk messagebox and exit
        messagebox.showerror('Error', _not_found_msg)
        sys.exit(0)
    game_module = module_from_name(mem.process_handle, 'ff7remake_.exe').lpBaseOfDll

    ### Pointers

    # Base
    if settings.GAME_VERSION == 'epic':
        player_base = game_module + 0x579D6E8
        data_base = game_module + 0x57F75B8
    elif GAME_VERSION == 'steam':
        player_base = game_module + 0x57A57E8
        data_base = game_module + 0x57F75B8

#base_3 = game_module + 0x0579DAE8 #'Somewhat' interchangeable with player_base; see notes on converting pointers.

### Helper functions

def getPtrAddr(base: int, offsets: List[int]) -> int:
    ''' Get pointer address. This version works with ASLR enabled in OS. 
    Args: 
        <base>: Base address.
        <offsets>: List of offsets.
    '''
    remote_pointer = RemotePointer(mem.process_handle, base)
    for offset in offsets:
        if offset != offsets[-1]:
            remote_pointer = RemotePointer(mem.process_handle, remote_pointer.value + offset)
        else:
            return remote_pointer.value + offset

# Read a value (uint)
# Un-used - for testing
'''
def read_uint(base, offsets: List[int]) -> int:
    value: cython.uint = mem.read_uint(getPtrAddr(base, offsets))
    return value
'''

# Highlight cheat label for a few seconds. (starts a thread to avoid blocking)
def temp_highlight(labels: list, new_color=settings.Appearance.ACTIVE, normal_color=settings.Appearance.FG) -> None:
    """ Temporarily highlight foreground color of a widget, then return to previous color.
    Call when executing one-off cheats to indicate cheat usage """

    def highlight():
        for label in labels:
            label.config(fg=new_color)
        sleep(settings.Appearance.FEEDBACK_COOLDOWN)
        for label in labels:
            label.config(fg=normal_color)

    # Launch highlight() as a thread
    hl_thread = Thread(target = highlight, daemon = True).start()

# Highlight cheat label background for a few seconds. (starts a thread to avoid blocking)
def temp_highlight_bg(labels: list, new_color=settings.Appearance.ACTIVE, normal_color=settings.Appearance.BG) -> None:
    """ Temporarily highlight background color of a widget.
    Call when executing one-off cheats to indicate cheat usage """

    def highlight():
        for label in labels:
            label.config(bg=new_color)
        sleep(settings.Appearance.FEEDBACK_COOLDOWN)
        for label in labels:
            label.config(bg=normal_color)

    # Launch highlight() as a thread
    hl_thread = Thread(target = highlight, daemon = True).start()

# Same as above, with arbitrary widget property. Test some partial functions using this as base:
def temp_change_property(labels: list, label_property, new_color: str = settings.Appearance.ACTIVE, normal_color: str = settings.Appearance.FG) -> None:
    """ Temporarily change a property of a widget.
    Call when executing one-off cheats, to indicate cheat usage. """

    def highlight():
        for label in labels:
            #label.config(prop=new_color)
            label[label_property] = new_color
        sleep(settings.Appearance.FEEDBACK_COOLDOWN)
        for label in labels:
            #label.config(prop=normal_color)
            label[label_property] = normal_color

    # Launch highlight() as a thread
    hl_thread = Thread(target = highlight, daemon = True).start()

# Update cheat label's text color (permanent).
# un-used / testing
def update_label_color(color: str, *labels) -> None:
    for label in labels:
        label.config(fg=color)

# Custom timed version of @lru_cache
# Reference: https://gist.github.com/Morreski/c1d08a3afa4040815eafd3891e16b945
def timed_cache(**timedelta_kwargs):
    '''Timed version of @lru_cache. Use on some getters to minimize repeatedly reading memory.'''

    def _wrapper(f):
        update_delta = timedelta(**timedelta_kwargs)
        next_update = datetime.now() + update_delta
        # Apply @lru_cache to f with no cache size limit
        f = functools.lru_cache(None)(f)

        @functools.wraps(f)
        def _wrapped(*args, **kwargs):
            nonlocal next_update
            now = datetime.now()
            if now >= next_update:
                f.cache_clear()
                next_update = now + update_delta
            return f(*args, **kwargs)
        return _wrapped
    return _wrapper

### Player class, to represent the player for i.e. inventory/settings
class Player():
    ''' Player class, to represent the player for i.e. inventory and meta settings that arent
    directly related to individual characters. '''

    def __init__(self, offsets: dict):
        # See offsets.py for offsets
        self.offsets = offsets
        # Flags for toggling meta cheats
        self.hard_mode_ap_multiplier_on: cython.bint = False
        self.hard_mode_exp_multiplier_on: cython.bint = False

    @property
    @timed_cache(minutes=1)
    def hard_mode(self) -> bool:
        '''Hard mode getter. True if hard mode, else False.'''
        _: cython.ushort = mem.read_ushort(getPtrAddr(player_base, self.offsets['hard_mode']))
        return bool(_)

    @property
    @timed_cache(minutes=1)
    def atb_per_slot(self) -> int:
        '''ATB per bar. (Getter)'''
        _: cython.uint = mem.read_uint(getPtrAddr(data_base, self.offsets['atb_per_slot']))
        return _

    @property
    @timed_cache(minutes=1)
    def player_atb_rate(self) -> float:
        '''Player ATB rate. (Getter)'''
        _: cython.float = mem.read_float(getPtrAddr(data_base, self.offsets['player_atb_rate']))
        return _

    @property
    @timed_cache(minutes=1)
    def ai_atb_rate(self) -> float:
        '''AI ATB rate. (getter)'''
        _: cython.float = mem.read_float(getPtrAddr(data_base, self.offsets['ai_atb_rate']))
        return _

    @property
    #@timed_cache(minutes=1)
    def hard_mode_exp_multiplier(self) -> int:
        '''Hard mode experience multiplier. (Getter) Default=200.'''
        _: cython.uint = mem.read_uint(getPtrAddr(data_base, self.offsets['hard_mode_exp_multiplier']))
        return _

    @property
    #@timed_cache(minutes=1)
    def hard_mode_ap_multiplier(self) -> int:
        '''Hard mode AP multiplier. (Getter) Default=300.'''
        _: cython.uint = mem.read_uint(getPtrAddr(data_base, self.offsets['hard_mode_ap_multiplier']))
        return _

    @property
    def play_time(self) -> int:
        '''Play time. (Getter)'''
        _: cython.uint = mem.read_uint(getPtrAddr(player_base, self.offsets['play_time']))
        return _

    # Controlled character getter (1 byte. offset from player_base)
    @property
    def controlled_character(self) -> str:
        ''' Return name of controlled character. 
        0=Cloud, 1=Barret, 2=Tifa, 3=Aerith, 4=Red, 5=Yuffie, 6=Sonon. '''
        _value = mem.read_bytes(getPtrAddr(player_base, self.offsets['controlled_char']), 1)
        _value = int.from_bytes(_value, 'big')
        _char_mappings = {
            0: 'Cloud',
            1: 'Barret',
            2: 'Tifa',
            3: 'Aerith',
            4: 'Red',
            5: 'Yuffie',
            6: 'Sonon',
        }
        _char_name = _char_mappings[_value]
        return _char_name

    # Set ATB per slot. (uint, 4 bytes)
    @atb_per_slot.setter
    def atb_per_slot(self, _target: int) -> None:
        ''' ATB per slot. (Setter) '''
        mem.write_uint(getPtrAddr(data_base, self.offsets['atb_per_slot']), _target)

    # Player atb rate setter (float)
    @player_atb_rate.setter
    def player_atb_rate(self, _target: float) -> None:
        ''' Player ATB Rate setter. '''
        mem.write_float(getPtrAddr(data_base, self.offsets['player_atb_rate']), _target)

    # AI atb rate setter (float)
    @ai_atb_rate.setter
    def ai_atb_rate(self, _target: float) -> None:
        ''' AI ATB Rate setter. '''
        mem.write_float(getPtrAddr(data_base, self.offsets['ai_atb_rate']), _target)

    # Hardmode EXP mult setter (uint 4bytes)
    @hard_mode_exp_multiplier.setter
    def hard_mode_exp_multiplier(self, _target) -> None:
        ''' Hardmode experience multiplier (Setter). Default=200 '''
        mem.write_uint(getPtrAddr(data_base, self.offsets['hard_mode_exp_multiplier']), _target)

    # Hardmode AP mult setter (4bytes uint)
    @hard_mode_ap_multiplier.setter
    def hard_mode_ap_multiplier(self, _target) -> None:
        ''' Hardmode AP multiplier (Setter). Default=300 '''
        mem.write_uint(getPtrAddr(data_base, self.offsets['hard_mode_ap_multiplier']), _target)

    """
    # context manager for AP mult - ensure value gets set back to default in case of crash/reload game
    # Not used.
    @contextlib.contextmanager
    def reset_ap_multiplier(self, _default_value):
        try:
            yield
        finally:
            self.hard_mode_ap_multiplier = _default_value

    # Test: context manager for arbitrary property
    # Not used yet.
    @contextlib.contextmanager
    def reset_property(self, _property, _default_value):
        try:
            yield
        finally:
            _property = _default_value
    """

    ## CHEATS - META

    @staticmethod
    def give_arbitrary_item(_item_name: cython.unicode, _item_offsets: List[int], _num: cython.uint = 1) -> None:
        '''Give an arbitrary item. Called by GUI optionmenu.
            Args:
                _item_name: Name of item, as in offsets.item_offsets[]
                _item_offsets: The item's offsets, as in offsets.item_offsets[]
                _num: Quantity to give
        '''
        _current_inv: cython.uint = mem.read_uint(getPtrAddr(player_base, _item_offsets))
        #_num = int(_num)
        # Don't write >99 of any item, except for Gil
        _new_qty: cython.uint = min(_current_inv + _num, 99) if not _item_offsets == Offsets.item_offsets['Gil'] else _current_inv + _num

        _msg = f'Current qty: {_current_inv} {_item_name}; adding {_num}. New qty: {_new_qty}'
        logging.debug(_msg)
        mem.write_uint(getPtrAddr(player_base, _item_offsets), _new_qty)

    def toggle_hard_mode_ap_multiplier(self) -> None:
        '''Boost hardmode AP multiplier (20x), for quick leveling of materia.
        Toggle cheat by setting a variable (hard_mode_ap_multiplier_on = True/False) -
        i.e. no event+daemon like the character cheats use.
        Game will overwrite value eventually.'''
        _default_mult: cython.uint = 300
        _cheat_mult: cython.uint = 6000
        logging.debug(f'Current hardmode AP mult: {self.hard_mode_ap_multiplier}.')

        # Check for hardmode first. If not hardmode then do nothing.
        if self.hard_mode: 
            # If ON, turn OFF
            if self.hard_mode_ap_multiplier_on == True or self.hard_mode_ap_multiplier == _cheat_mult:
                self.hard_mode_ap_multiplier_on = False
                self.hard_mode_ap_multiplier = _default_mult
                # Update GUI
                for _ in (ct_gui.hardmode_ap_multiplier_label, ct_gui.hardmode_ap_multiplier_effect_label):
                    _.config(foreground=settings.Appearance.FG)
                logging.debug(f'AP Multiplier boost OFF. Reset to {_default_mult}')
            # If OFF, turn ON
            elif self.hard_mode_ap_multiplier_on == False:
                self.hard_mode_ap_multiplier_on = True
                self.hard_mode_ap_multiplier = _cheat_mult
                # Update GUI
                for _ in (ct_gui.hardmode_ap_multiplier_label, ct_gui.hardmode_ap_multiplier_effect_label):
                    _.config(foreground=settings.Appearance.ACTIVE)
                logging.debug('AP Multiplier boost ON')
        else:
            logging.warning('Not playing Hard Mode! Skipping AP mult cheat.')
            ct_gui.log_error('Not playing Hard Mode!') #Display message on trainer
            # In case it gets left at cheat value when reloading etc, go ahead and check+reset
            if self.hard_mode_ap_multiplier == _cheat_mult:
                self.hard_mode_ap_multiplier = _default_mult

    def toggle_hard_mode_exp_multiplier(self) -> None:
        '''Boost hardmode EXP multiplier (x20), for quick leveling of characters.
        Toggle cheat by simply setting an instance variable - no event flag like characters cheats use.
        Game doesn't overwrite EXP mult as quickly as AP - ensure it gets reset if crash/reload;
        try using a context manager.'''
        _default_mult: cython.uint = 200
        _cheat_mult: cython.uint = 4000
        logging.debug(f'Current hardmode EXP multiplier: {self.hard_mode_exp_multiplier}.')

        # Check for hardmode first.
        if self.hard_mode:
            # If cheat ON, turn OFF
            if self.hard_mode_exp_multiplier_on == True or self.hard_mode_exp_multiplier == _cheat_mult:
                self.hard_mode_exp_multiplier_on = False
                self.hard_mode_exp_multiplier = _default_mult
                # Update GUI
                for _ in (ct_gui.hardmode_exp_multiplier_label, ct_gui.hardmode_exp_multiplier_effect_label):
                    _.config(foreground=settings.Appearance.FG)
                logging.debug(f'EXP Multiplier boost OFF. Reset to {_default_mult}')
            # If OFF, turn ON
            elif self.hard_mode_exp_multiplier_on == False:
                self.hard_mode_exp_multiplier_on = True
                self.hard_mode_exp_multiplier = _cheat_mult
                # Update GUI
                for _ in (ct_gui.hardmode_exp_multiplier_label, ct_gui.hardmode_exp_multiplier_effect_label):
                    _.config(foreground=settings.Appearance.ACTIVE)
                logging.debug('EXP Multiplier boost ON')
        else:
            #If not hard mode, don't do anything.
            logging.warning('Not playing Hard Mode! Skipping EXP mult cheat.')
            ct_gui.log_error('Not playing Hard Mode!') #Display message on trainer
            # In case it gets left at cheat value when reloading etc, go ahead and check+reset
            if self.hard_mode_exp_multiplier == _cheat_mult:
                self.hard_mode_exp_multiplier = _default_mult

# It's YOU, get it?
you = Player(
    offsets = Offsets.Meta,
)

### Create a class to use for party members
class PartyMember():
    ### Class variables:

    #all_characters: list = [] #List containing each instance (each party character). For all_chars cheats
    all_characters: set = set()

    # Cheat-toggle class variables
    all_godmode_on: cython.bint = False
    all_inf_mp_on: cython.bint = False
    all_inf_atb_on: cython.bint = False
    all_inf_limit_on: cython.bint = False
    all_atk_boost_on: cython.bint = False
    all_luck_boost_on: cython.bint = False

    # Cheat thread stop events
    all_godmode_stop_event = Event() #set this event to stop godmode thread
    all_inf_mp_stop_event = Event()
    all_inf_atb_stop_event = Event()
    all_inf_limit_stop_event = Event()
    all_atk_boost_stop_event = Event()
    all_luck_boost_stop_event = Event()

    # GUI labels for "all-chars" cheats
    ''' 
    # Right now this is breaking because ct_gui isn't initialized yet.
    all_gui_labels = {
        'godmode': (ct_gui.all_chars_godmode_label, ct_gui.all_chars_godmode_effect_label),
        'inf_mp': (ct_gui.all_chars_inf_mp_label, ct_gui.all_chars_inf_mp_effect_label),
        'inf_atb': (ct_gui.all_chars_inf_atb_label, ct_gui.all_chars_inf_atb_effect_label),
    }
    '''

    @classmethod
    def current_party(cls) -> set:
        '''Return a set of all characters currently in party.'''
        _p: set = {_ for _ in cls.all_characters if _.in_party}
        return _p

    @classmethod
    def heal_all(cls) -> None:
        '''Heal all characters in party.'''
        for _ in cls.all_characters:
            if _.in_party:
                _.heal()

    @classmethod
    def all_mp_refill(cls) -> None:
        '''MP refill all chars in party.'''
        for _ in cls.all_characters:
            if _.in_party:
                _.mp_refill()

    @classmethod
    def all_atb_refill(cls) -> None:
        '''ATB refill, all characters.'''
        for _ in cls.all_characters:
            if _.in_party:
                _.atb_refill()

    @classmethod
    def all_limit_refill(cls) -> None:
        '''Limit refill, all chars.'''
        for _ in cls.all_characters:
            if _.in_party:
                _.limit_refill()
    
    @classmethod
    def all_atk_boost(cls) -> None:
        '''Boost attack values, all chars. Effect is temporary; game will quickly re-calculate.'''
        for _ in cls.all_characters:
            if _.in_party:
                _.atk_boost()

    @classmethod
    def all_luck_boost(cls) -> None:
        '''Boost luck value, all chars. Effect is temporary; game will quickly re-calculate.'''
        #for _ in cls.all_characters:
        #    if _.in_party:
        #        _.luck = 255
        for _ in cls.current_party():
            _.luck = 255

    # TEST ALL CHARS GODMODE LOOP
    @classmethod
    def all_godmode_loop(cls) -> None:
        '''Godmode loop (all chars). Should be launched in a thread.'''
        logging.debug('Launching godmode loop (all characters) ...')
        while True:
            if cls.all_godmode_stop_event.is_set(): #if stop event is set, then break from the loop.
                logging.debug('Breaking godmode loop (all)..')
                break
            cls.heal_all()
            sleep(1)

    # All chars Inf MP loop
    @classmethod
    def all_inf_mp_loop(cls) -> None:
        '''Infinite MP loop (all chars). Should be launched in a thread.'''
        logging.debug('Launching Inf MP loop (all characters) ...')
        while True:
            if cls.all_inf_mp_stop_event.is_set(): #if stop event is set, then break from the loop.
                logging.debug('Breaking Inf MP loop (all)..')
                break
            cls.all_mp_refill()
            sleep(5)

    # All chars Inf ATB loop
    @classmethod
    def all_inf_atb_loop(cls) -> None:
        '''Infinite ATB loop (all chars). Should be launched in a thread. Fill ATB of all characters, every n seconds. '''
        logging.debug('Launching Inf ATB loop (all characters) ...')
        while True:
            if cls.all_inf_atb_stop_event.is_set(): #if stop event is set, then break from the loop.
                logging.debug('Breaking Inf ATB loop (all)..')
                break
            cls.all_atb_refill()
            sleep(5)

    # All chars Inf Limit loop
    @classmethod
    def all_inf_limit_loop(cls) -> None:
        '''Infinite Limit loop (all chars). Should be launched in a thread. Fills limit gauge of all characters, every n seconds. '''
        logging.debug('Launching Inf Limit loop (all characters) ...')
        while True:
            if cls.all_inf_limit_stop_event.is_set(): #if stop event is set, then break from the loop.
                logging.debug('Breaking Inf Limit loop (all)..')
                break
            cls.all_limit_refill()
            sleep(5)

    # All chars Atk Boost loop
    @classmethod
    def all_atk_boost_loop(cls) -> None:
        '''Attack Boost loop (all chars). Write atk + magic atk values every n seconds. Should be launched in a thread.'''
        logging.debug('Launching Atk Boost loop (all characters) ...')
        while True:
            if cls.all_atk_boost_stop_event.is_set():
                logging.debug('Breaking Atk Boost loop (all)...')
                break
            cls.all_atk_boost()
            sleep(2)

    # All chars Luck Boost loop
    @classmethod
    def all_luck_boost_loop(cls) -> None:
        '''Luck Boost loop (all chars). Write Luck value every n secs. Should be launched in a thread.'''
        logging.debug('Launching Luck Boost loop (all characters) ...')
        while True:
            if cls.all_luck_boost_stop_event.is_set():
                logging.debug('Breaking Luck Boost loop (all)...')
                break
            cls.all_luck_boost()
            sleep(2)


    # TEST ALL CHARS GODMODE TOGGLE
    @classmethod
    def all_toggle_godmode(cls) -> None:
        '''Toggle Godmode on/off - ALL CHARS.'''
        if cls.all_godmode_on == True:
            # If on, turn it off
            cls.all_godmode_on = False
            cls.all_godmode_stop_event.set()
            # Update the gui labels
            #for _ in cls.all_gui_labels['godmode']:
            for _ in (ct_gui.all_chars_godmode_label, ct_gui.all_chars_godmode_effect_label):
                _.config(foreground=settings.Appearance.FG)
        elif cls.all_godmode_on == False:
            # If off, turn it on
            cls.all_godmode_on = True
            cls.all_godmode_stop_event.clear()
            Thread(target=cls.all_godmode_loop, daemon=True).start()
            # Update the gui labels
            #for _ in cls.all_gui_labels['godmode']:
            for _ in (ct_gui.all_chars_godmode_label, ct_gui.all_chars_godmode_effect_label):
                _.config(foreground=settings.Appearance.ACTIVE)
            logging.debug(f'Toggled godmode ON (ALL chars)')

    # TEST ALL CHARS Inf MP TOGGLE
    @classmethod
    def all_toggle_inf_mp(cls) -> None:
        '''Toggle Infinite MP on/off - ALL CHARS.'''
        if cls.all_inf_mp_on == True:
            # If on, turn it off
            cls.all_inf_mp_on = False
            cls.all_inf_mp_stop_event.set()
            # Update the gui labels
            for _ in (ct_gui.all_chars_inf_mp_label, ct_gui.all_chars_inf_mp_effect_label):
                _.config(foreground=settings.Appearance.FG)
        elif cls.all_inf_mp_on == False:
            # If off, turn it on
            cls.all_inf_mp_on = True
            cls.all_inf_mp_stop_event.clear()
            Thread(target=cls.all_inf_mp_loop, daemon=True).start()
            # Update the gui labels
            for _ in (ct_gui.all_chars_inf_mp_label, ct_gui.all_chars_inf_mp_effect_label):
                _.config(foreground=settings.Appearance.ACTIVE)
            logging.debug('Toggled Inf MP ON (All chars)')

    # Toggle Inf ATB all chars
    @classmethod
    def all_toggle_inf_atb(cls) -> None:
        '''Toggle Infinite ATB on/off - ALL CHARS.'''
        if cls.all_inf_atb_on == True:
            # If on, turn it off
            cls.all_inf_atb_on = False
            cls.all_inf_atb_stop_event.set()
            # Update the gui labels
            for _ in (ct_gui.all_chars_inf_atb_label, ct_gui.all_chars_inf_atb_effect_label):
                _.config(foreground=settings.Appearance.FG)
        elif cls.all_inf_atb_on == False:
            # If off, turn it on
            cls.all_inf_atb_on = True
            cls.all_inf_atb_stop_event.clear()
            Thread(target=cls.all_inf_atb_loop, daemon=True).start()
            # Update the gui labels
            for _ in (ct_gui.all_chars_inf_atb_label, ct_gui.all_chars_inf_atb_effect_label):
                _.config(foreground=settings.Appearance.ACTIVE)
            logging.debug('Toggled Inf ATB ON (All chars)')

    # Toggle Inf Limit all chars
    @classmethod
    def all_toggle_inf_limit(cls) -> None:
        '''Toggle Infinite Limit Break on/off - ALL CHARS.'''
        if cls.all_inf_limit_on == True:
            # If on, turn it off
            cls.all_inf_limit_on = False
            cls.all_inf_limit_stop_event.set()
            # Update the gui labels
            for _ in (ct_gui.all_chars_inf_limit_label, ct_gui.all_chars_inf_limit_effect_label):
                _.config(foreground=settings.Appearance.FG)
        elif cls.all_inf_limit_on == False:
            # If off, turn it on
            cls.all_inf_limit_on = True
            cls.all_inf_limit_stop_event.clear()
            Thread(target=cls.all_inf_limit_loop, daemon=True).start()
            # Update the gui labels
            for _ in (ct_gui.all_chars_inf_limit_label, ct_gui.all_chars_inf_limit_effect_label):
                _.config(foreground=settings.Appearance.ACTIVE)
            logging.debug('Toggled Inf Limit ON (All chars)')

    # Toggle Atk Boost all chars
    @classmethod
    def all_toggle_atk_boost(cls) -> None:
        '''Toggle Attack Boost on/off - ALL CHARS.'''
        if cls.all_atk_boost_on == True:
            # If on, turn it off
            cls.all_atk_boost_on = False
            cls.all_atk_boost_stop_event.set()
            # Update the gui labels
            for _ in (ct_gui.all_chars_atk_boost_label, ct_gui.all_chars_atk_boost_effect_label):
                _.config(foreground=settings.Appearance.FG)
            logging.debug('Toggled Attack Boost OFF (All chars)')
        elif cls.all_atk_boost_on == False:
            # If off, turn it on
            cls.all_atk_boost_on = True
            cls.all_atk_boost_stop_event.clear()
            Thread(target=cls.all_atk_boost_loop, daemon=True).start()
            # Update the gui labels
            for _ in (ct_gui.all_chars_atk_boost_label, ct_gui.all_chars_atk_boost_effect_label):
                _.config(foreground=settings.Appearance.ACTIVE)
            logging.debug('Toggled Attack Boost ON (All chars)')

    # Toggle Luck Boost all chars
    @classmethod
    def all_toggle_luck_boost(cls) -> None:
        '''Toggle Luck Boost on/off - ALL CHARS.'''
        if cls.all_luck_boost_on == True:
            # If on, turn it off
            cls.all_luck_boost_on = False
            cls.all_luck_boost_stop_event.set()
            # Update the gui labels
            for _ in (ct_gui.all_chars_luck_boost_label, ct_gui.all_chars_luck_boost_effect_label):
                _.config(foreground=settings.Appearance.FG)
            logging.debug('Toggled Luck Boost OFF (All chars)')
        elif cls.all_luck_boost_on == False:
            # If off, turn it on
            cls.all_luck_boost_on = True
            cls.all_luck_boost_stop_event.clear()
            Thread(target=cls.all_luck_boost_loop, daemon=True).start()
            # Update the gui labels
            for _ in (ct_gui.all_chars_luck_boost_label, ct_gui.all_chars_luck_boost_effect_label):
                _.config(foreground=settings.Appearance.ACTIVE)
            logging.debug('Toggled Luck Boost ON (All chars)')

    def __init__(self, char_name: str, offsets: dict, gui_labels: dict):
        self.char_name = char_name
        self.offsets = offsets # Dict of character's stat offsets
        self.gui_labels = gui_labels #Dict of GUI labels that apply to each stat

        # Cheat bools
        self.godmode_on: cython.bint = False
        self.inf_mp_on: cython.bint = False
        self.inf_atb_on: cython.bint = False
        self.atk_boost_on: cython.bint = False
        self.inf_limit_on: cython.bint = False

        # Cheat thread stop events
        self.godmode_stop_event = Event() #set this event to stop godmode thread
        self.inf_mp_stop_event = Event()
        self.inf_atb_stop_event = Event()
        self.atk_boost_stop_event = Event()
        self.inf_limit_stop_event = Event()

        # Append self to list of party characters
        PartyMember.all_characters.add(self)

    # Current HP getter
    @property
    def current_hp(self) -> cython.ushort:
        '''Return current HP.'''
        return mem.read_ushort(getPtrAddr(player_base, self.offsets['hp']))

    # Max HP getter
    @property
    @timed_cache(seconds=30)
    def max_hp(self) -> int:
        '''Return max HP.'''
        return mem.read_ushort(getPtrAddr(player_base, self.offsets['max_hp']))

    # Current MP Getter
    @property
    def current_mp(self) -> int:
        '''Return current MP.'''
        return mem.read_ushort(getPtrAddr(player_base, self.offsets['mp']))

    # Max MP getter
    @property
    @timed_cache(seconds=30)
    def max_mp(self) -> int:
        return mem.read_ushort(getPtrAddr(player_base, self.offsets['max_mp']))

    # ATB Getter
    @property
    def current_atb(self) -> float:
        return mem.read_float(getPtrAddr(player_base, self.offsets['atb']))

    # ATB SLOTS Getter
    @property
    @timed_cache(seconds=10)
    def atb_slots(self) -> int:
        '''Number of ATB bars.'''
        _ = mem.read_bytes(getPtrAddr(player_base, self.offsets['atb_slots']), 1)
        _ = int.from_bytes(_, 'big')
        return _

    # Limit break getter
    @property
    def current_limit(self) -> float:
        '''Limit break bar.'''
        return mem.read_float(getPtrAddr(player_base, self.offsets['limit']))

    # Atk getter
    @property
    @timed_cache(seconds=20)
    def atk(self) -> int:
        '''Physical attack value.'''
        return mem.read_ushort(getPtrAddr(player_base, self.offsets['p_atk']))

    # Magic atk getter
    @property
    @timed_cache(seconds=20)
    def magic_atk(self) -> int:
        '''Magic attack value.'''
        return mem.read_ushort(getPtrAddr(player_base, self.offsets['m_atk']))

    # Luck getter
    @property
    @timed_cache(minutes=1)
    def luck(self) -> int:
        '''Return Luck value.'''
        return mem.read_ushort(getPtrAddr(player_base, self.offsets['luck']))

    # Str getter
    @property
    @timed_cache(minutes=1)
    def strength(self) -> int:
        '''Return Strength value.'''
        _ = mem.read_bytes(getPtrAddr(player_base, self.offsets['strength']), 1)
        _ = int.from_bytes(x, 'big')
        return _

    # Def getter
    @property
    @timed_cache(minutes=1)
    def defense(self) -> int:
        '''Physical defense value.'''
        return mem.read_ushort(getPtrAddr(player_base, self.offsets['p_def']))

    # Mag Def getter
    @property
    @timed_cache(minutes=1)
    def mag_defense(self) -> int:
        '''Magic defense value.'''
        return mem.read_ushort(getPtrAddr(player_base, self.offsets['m_def']))

    # Currently in party
    @property
    @timed_cache(minutes=1)
    def in_party(self) -> bool:
        '''Return True if character is currently in party, else False.'''
        _value = mem.read_bytes(getPtrAddr(player_base, self.offsets['in_party']), 1)
        _value = int.from_bytes(_value, 'big')
        return True if _value == 1 else False

    # Current HP setter
    @current_hp.setter
    def current_hp(self, _target_hp: cython.ushort) -> None:
        mem.write_ushort(getPtrAddr(player_base, self.offsets['hp']), _target_hp)

    # Current MP setter
    @current_mp.setter
    def current_mp(self, _target_mp: cython.ushort) -> None:
        mem.write_ushort(getPtrAddr(player_base, self.offsets['mp']), _target_mp)

    # ATB setter
    @current_atb.setter
    def current_atb(self, _target_atb: cython.float) -> None:
        mem.write_float(getPtrAddr(player_base, self.offsets['atb']), _target_atb)

    # ATB Slots setter
    @atb_slots.setter
    def atb_slots(self, _target) -> None:
        ''' Buggy. Still working on this. '''
        _target = _target.to_bytes(1, 'big')
        mem.write_bytes(getPtrAddr(player_base, self.offsets['atb_slots']), value=_target, length=1)

    # Limit setter
    @current_limit.setter
    def current_limit(self, _target_value: cython.float) -> None:
        ''' Limit break bar (setter). '''
        mem.write_float(getPtrAddr(player_base, self.offsets['limit']), _target_value)

    # Physical ATK setter
    @atk.setter
    def atk(self, _target_value: cython.ushort) -> None:
        mem.write_ushort(getPtrAddr(player_base, self.offsets['p_atk']), _target_value)

    # Magic atk setter
    @magic_atk.setter
    def magic_atk(self, _target_value: cython.ushort) -> None:
        mem.write_ushort(getPtrAddr(player_base, self.offsets['m_atk']), _target_value)

    # Luck setter
    @luck.setter
    def luck(self, _target_value) -> None:
        mem.write_ushort(getPtrAddr(player_base, self.offsets['luck']), _target_value)

    ### Cheat methods

    # Heal
    def heal(self) -> None:
        '''Heal character to full HP.'''
        if self.current_hp < self.max_hp:
            self.current_hp = self.max_hp

    # Refill MP
    def mp_refill(self) -> None:
        '''Fill character's MP to full.'''
        if self.current_mp < self.max_mp:
            self.current_mp = self.max_mp

    # Fill ATB
    def atb_refill(self) -> None:
        '''Give character full ATB.'''
        # First check # of bars; if 2 bars then set to 2000, if 3 then 3000
        if self.current_atb < 2000.0:
            self.current_atb = 2000.0
    
    # Fill limit
    def limit_refill(self) -> None:
        '''Give character full limit.'''
        if self.current_limit < 1500.0:
            self.current_limit = 1500.0

    # Boost attack values
    def atk_boost(self, _target: cython.ushort = 2500) -> None:
        '''Boost both atk + magic atk. Temporary, game will recalculate quickly.'''
        if self.atk < _target or self.magic_atk < _target:
            self.atk = _target
            self.magic_atk = _target

    # godmode loop to launch as thread
    def godmode_loop(self) -> None:
        ''' Heal character, in a loop. '''
        logging.debug('Beginning a godmode loop...')
        while True:
            #if self.godmode_on == False: #Use events instead
            if self.godmode_stop_event.is_set(): #if stop event is set, then break from the loop.
                logging.debug('Breaking godmode loop..')
                break
            self.heal()
            sleep(1)

    def inf_mp_loop(self) -> None:
        '''Refill MP, in a loop.'''
        logging.debug('beginning MP loop...')
        while True:
            if self.inf_mp_stop_event.is_set():
                break
            self.mp_refill()
            sleep(5)

    def inf_atb_loop(self) -> None:
        '''Infinite ATB loop.'''
        logging.debug('beginning ATB loop...')
        while True:
            if self.inf_atb_stop_event.is_set():
                break
            self.atb_refill()
            sleep(4)

    def inf_limit_loop(self) -> None:
        '''Infinite Limit Break loop.'''
        logging.debug('Launching Inf Limit loop...')
        while True:
            if self.inf_limit_stop_event.is_set():
                break
            self.limit_refill()
            sleep(5)

    def atk_boost_loop(self) -> None:
        ''' Boost atk + magic atk. Effect is temporary as game will quickly re-calculate.'''
        logging.debug('Starting Attack boost loop ...')
        while True:
            if self.atk_boost_stop_event.is_set():
                break
            self.atk_boost()
            sleep(2)

    # Test version of the above loops, but with arbitrary stat to freeze. 
    #(un-used/testing)
    def freeze_stat_loop(self, _stop_event, _stat, _target_val) -> None:
        '''Freeze a given stat.'''
        logging.debug('Beginning a <cheat> loop')
        while True:
            if _stop_event.is_set():
                logging.debug('breaking loop...')
                break
            if _stat < _target_val:
                _stat = _target_val
            sleep(0.5)

    ### TOGGLES for cheat daemons
    def toggle_godmode(self):
        '''Toggle Godmode on/off + launch godmode thread. '''
        if self.godmode_on == True:
            # If on, turn it off
            self.godmode_on = False
            self.godmode_stop_event.set()
            # Update the gui label color
            for _ in self.gui_labels['godmode']:
                _.config(foreground=settings.Appearance.FG)
            # For testing
            logging.debug(f'Toggled godmode OFF ({self.char_name})')
        elif self.godmode_on == False:
            # If off, turn it on
            self.godmode_on = True
            self.godmode_stop_event.clear()
            #Thread(target=self.godmode_loop, args=(self.godmode_stop_event,), daemon=True).start()
            Thread(target=self.godmode_loop, daemon=True).start()
            # Update the gui label color
            for _ in self.gui_labels['godmode']:
                _.config(foreground=settings.Appearance.ACTIVE)
            logging.debug(f'Toggled godmode ON ({self.char_name})')

    def toggle_inf_mp(self):
        ''' Toggle Infinite MP for referenced character. '''
        if self.inf_mp_on == True:
            # If on, turn it off
            self.inf_mp_on = False
            self.inf_mp_stop_event.set()
            # Update the gui label color
            for _ in self.gui_labels['inf_mp']:
                _.config(foreground=settings.Appearance.FG)
            # For testing
            logging.debug(f'Toggled inf_mp OFF ({self.char_name})')
        elif self.inf_mp_on == False:
            # If off, turn it on
            self.inf_mp_on = True
            self.inf_mp_stop_event.clear()
            Thread(target=self.inf_mp_loop, daemon=True).start()
            # Update the gui label color
            for _ in self.gui_labels['inf_mp']:
                _.config(foreground=settings.Appearance.ACTIVE)
            # For testing/debug output
            logging.debug(f'Toggled inf_mp ON ({self.char_name})')

    def toggle_inf_atb(self):
        '''Toggle Infinite ATB.'''
        if self.inf_atb_on == True:
            # If on, turn it off
            self.inf_atb_on = False
            self.inf_atb_stop_event.set()
            # Update the gui label color
            for _ in self.gui_labels['inf_atb']:
                _.config(foreground=settings.Appearance.FG)
            # for testing
            logging.debug(f'Toggled inf_atb OFF ({self.char_name})')
        elif self.inf_atb_on == False:
            # If off, turn it on
            self.inf_atb_on = True
            self.inf_atb_stop_event.clear()
            Thread(target=self.inf_atb_loop, daemon=True).start()
            # Update the gui label color
            for _ in self.gui_labels['inf_atb']:
                _.config(foreground=settings.Appearance.ACTIVE)
            # For testing/debug output
            logging.debug(f'Toggled inf_atb ON ({self.char_name})')

    def toggle_inf_limit(self):
        '''Toggle infinite limit break.'''
        if self.inf_limit_on == True:
            # If on, turn it off
            self.inf_limit_on = False
            self.inf_limit_stop_event.set()
            # Update the gui label color
            for _ in self.gui_labels['inf_limit']:
                _.config(foreground=settings.Appearance.FG)
            # for testing
            logging.debug(f'Toggled inf_limit OFF ({self.char_name})')
        elif self.inf_limit_on == False:
            # If off, turn it on
            self.inf_limit_on = True
            self.inf_limit_stop_event.clear()
            Thread(target=self.inf_limit_loop, daemon=True).start()
            # Update the gui label color
            for _ in self.gui_labels['inf_limit']:
                _.config(foreground=settings.Appearance.ACTIVE)
            # For testing/debug output
            logging.debug(f'Toggled inf_limit ON ({self.char_name})')

    def toggle_atk_boost(self):
        '''Toggle physical+magic attack boost.'''
        if self.atk_boost_on == True:
            # If on, turn it off
            self.atk_boost_on = False
            self.atk_boost_stop_event.set()
            # Update the gui label color
            for _ in self.gui_labels['atk_boost']:
                _.config(foreground=settings.Appearance.FG)
            logging.debug(f'Toggled atk_boost OFF ({self.char_name})')
        elif self.atk_boost_on == False:
            # If off, turn it on
            self.atk_boost_on = True
            self.atk_boost_stop_event.clear()
            Thread(target=self.atk_boost_loop, daemon=True).start()
            # Update the gui label color
            for _ in self.gui_labels['atk_boost']:
                _.config(foreground=settings.Appearance.ACTIVE)
            # For testing/debug output
            logging.debug(f'Toggled atk_boost ON ({self.char_name})')

### GUI

class CheatTrainer():
    ''' The main GUI window. '''

    def __init__(self, window_title):

        self.is_hidden: cython.bint = False #For window hiding

        self.win = Tk()
        if settings.Appearance.FRAMELESS_WINDOW:
            self.win.overrideredirect(True)
        self.win.wm_attributes("-topmost", 1)
        self.win.wm_attributes("-alpha", settings.Appearance.ALPHA)
        self.win.columnconfigure(0, weight=1)
        self.win.columnconfigure(1, weight=1)

        ### APPEARANCE OPTIONS

        self.win.configure(background=settings.Appearance.BG)
        # Transparent BG on main window, if configured
        if settings.Appearance.TRANSPARENT_BG:
            self.win.wm_attributes('-transparentcolor', settings.Appearance.BG)

        # Add some default widget options, to reduce repeating styles. Use values from settings.py
        self.win.option_add("*Font", (settings.Appearance.FONTS['TEXT'], settings.Appearance.FONTS['FONT_SIZE']))

        self.win.option_add("*Label*Background", settings.Appearance.BG)
        self.win.option_add("*Label*Foreground", settings.Appearance.FG)
        self.win.option_add("*Label*Font", (settings.Appearance.FONTS['TEXT'], settings.Appearance.FONTS['FONT_SIZE']))

        # If transparent_bg set, then set a bg color for buttons. Otherwise they'll be buggy
        if settings.Appearance.TRANSPARENT_BG:
            self.win.option_add("*Button*Background", settings.Appearance.BG_ENTRY)
        else:
            self.win.option_add("*Button*Background", settings.Appearance.BG)
        self.win.option_add("*Button*Foreground", settings.Appearance.FG)
        self.win.option_add("*Button*Font", (settings.Appearance.FONTS['TEXT'], settings.Appearance.FONTS['FONT_SIZE']))
        self.win.option_add("*Button*BorderWidth", 1)
        self.win.option_add("*Button*Relief", "solid")

        ### WIDGETS

        ## Title label
        self.title_label = Label(self.win, text=window_title, font=(settings.Appearance.FONTS['TITLE'], settings.Appearance.FONTS['FONT_SIZE_TITLE']), foreground=settings.Appearance.BLUE)
        self.title_label.grid(column=0, row=1, sticky='news', padx=48, columnspan=2)

        self.author_label = Label(self.win, text='By rogueautomata')
        self.author_label.grid(column=0, row=2, sticky='news', padx=48, columnspan=2)

        # Image
        if settings.Appearance.SHOW_IMAGE:
            try:
                self.image = PhotoImage(file=settings.Appearance.HEADER_IMG_PATH)
                self.image_label = Label(image=self.image, background=settings.Appearance.BG, height=140)
                self.image_label.grid(column=0, row=3, sticky='news', columnspan=2)
            except:
                logging.error(f'Image file not found: {settings.Appearance.HEADER_IMG_PATH}')
        else:
            # Create a label with similar width to keep things neat.
            self.image_label = Label(background=settings.Appearance.BG, width=38)
            self.image_label.grid(column=0, row=3, sticky='news', columnspan=2)

        ## Info labels
        self.hotkeys_label = Label(self.win, text='Hotkey', font=(settings.Appearance.FONTS['TITLE'], settings.Appearance.FONTS['FONT_SIZE_TITLE']), foreground=settings.Appearance.BLUE)
        self.effect_label = Label(self.win, text='Effect', font=(settings.Appearance.FONTS['TITLE'], settings.Appearance.FONTS['FONT_SIZE_TITLE']), foreground=settings.Appearance.BLUE)

        self.hotkeys_label.grid(column=0, row=5, sticky='wns', pady=(0,16))
        self.effect_label.grid(column=1, row=5, sticky='wns', pady=(0,16))

        ## Hotkeys labels ##

        if settings.Appearance.ENABLE_INDIVIDUAL_CHARS:
            ## Optional - Cheats for individual characters

            # Cloud Godmode
            self.cloud_godmode_label = Label(self.win, text=settings.HOTKEYS['CLOUD_GODMODE'])
            self.cloud_godmode_label.grid(column=0, row=10, sticky='wns')

            self.cloud_godmode_effect_label = Label(self.win, text="Cloud Godmode")
            self.cloud_godmode_effect_label.grid(column=1, row=10, sticky='wns')

            ## Cloud Inf MP button
            self.mp_label = Label(self.win, text=settings.HOTKEYS['CLOUD_INF_MP'])
            self.mp_label.grid(column=0, row=11, sticky='wns')

            self.mp_effect_label = Label(self.win, text="Cloud Inf MP")
            self.mp_effect_label.grid(column=1, row=11, sticky='wns')

            # Cloud Inf ATB
            self.cloud_atb_label = Label(self.win, text=settings.HOTKEYS['CLOUD_INF_ATB'])
            self.cloud_atb_label.grid(column=0, row=12, sticky='wns')

            self.atb_effect_label = Label(self.win, text="Cloud Inf ATB")
            self.atb_effect_label.grid(column=1, row=12, sticky='wns')

            # Cloud Attack boost
            self.cloud_atk_boost_label = Label(self.win, text=settings.HOTKEYS['CLOUD_ATK_BOOST'])
            self.cloud_atk_boost_label.grid(column=0, row=13, sticky='wns')

            self.cloud_atk_boost_effect_label = Label(self.win, text="Cloud Attack Boost")
            self.cloud_atk_boost_effect_label.grid(column=1, row=13, sticky='wns')

            # Spacer
            self.spacer01 = Label(self.win).grid(column=0, row=16, columnspan=2)

            ### Aerith labels
            self.aerith_godmode_label = Label(self.win, text=settings.HOTKEYS['AERITH_GODMODE'])
            self.aerith_godmode_label.grid(column=0, row=20, sticky='wns')

            self.aerith_godmode_effect_label = Label(self.win, text="Aerith Godmode")
            self.aerith_godmode_effect_label.grid(column=1, row=20, sticky='wns')

            self.aerith_inf_mp_label = Label(self.win, text=settings.HOTKEYS['AERITH_INF_MP'])
            self.aerith_inf_mp_label.grid(column=0, row=21, sticky='wns')

            self.aerith_inf_mp_effect_label = Label(self.win, text="Aerith Inf MP")
            self.aerith_inf_mp_effect_label.grid(column=1, row=21, sticky='wns')

            self.aerith_inf_atb_label = Label(self.win, text=settings.HOTKEYS['AERITH_INF_ATB'])
            self.aerith_inf_atb_label.grid(column=0, row=22, sticky='wns')

            self.aerith_inf_atb_effect_label = Label(self.win, text="Aerith Inf ATB")
            self.aerith_inf_atb_effect_label.grid(column=1, row=22, sticky='wns')

            # Spacer
            self.spacer02 = Label(self.win).grid(column=0, row=25, columnspan=2)

        ### All-characters cheats
        # godmode all
        self.all_chars_godmode_label = Label(self.win, text=settings.HOTKEYS['ALL_CHARS_GODMODE'])
        self.all_chars_godmode_label.grid(column=0, row=50, sticky='wns')

        self.all_chars_godmode_effect_label = Label(self.win, text="All Godmode")
        self.all_chars_godmode_effect_label.grid(column=1, row=50, sticky='wns')

        # Inf MP all
        self.all_chars_inf_mp_label = Label(self.win, text=settings.HOTKEYS['ALL_CHARS_INF_MP'])
        self.all_chars_inf_mp_label.grid(column=0, row=51, sticky='wns')

        self.all_chars_inf_mp_effect_label = Label(self.win, text="All Inf MP")
        self.all_chars_inf_mp_effect_label.grid(column=1, row=51, sticky='wns')

        # Inf ATB all
        self.all_chars_inf_atb_label = Label(self.win, text=settings.HOTKEYS['ALL_CHARS_INF_ATB'])
        self.all_chars_inf_atb_label.grid(column=0, row=52, sticky='wns')

        self.all_chars_inf_atb_effect_label = Label(self.win, text="All Inf ATB")
        self.all_chars_inf_atb_effect_label.grid(column=1, row=52, sticky='wns')

        # Inf Limit all
        self.all_chars_inf_limit_label = Label(self.win, text=settings.HOTKEYS['ALL_CHARS_INF_LIMIT'])
        self.all_chars_inf_limit_label.grid(column=0, row=53, sticky='wns')

        self.all_chars_inf_limit_effect_label = Label(self.win, text="All Inf Limit")
        self.all_chars_inf_limit_effect_label.grid(column=1, row=53, sticky='wns')

        # Attack Boost all
        self.all_chars_atk_boost_label = Label(self.win, text=settings.HOTKEYS['ALL_CHARS_ATK_BOOST'])
        self.all_chars_atk_boost_label.grid(column=0, row=54, sticky='wns')

        self.all_chars_atk_boost_effect_label = Label(self.win, text="All Attack Boost")
        self.all_chars_atk_boost_effect_label.grid(column=1, row=54, sticky='wns')

        # Luck Boost all
        self.all_chars_luck_boost_label = Label(self.win, text=settings.HOTKEYS['ALL_CHARS_LUCK_BOOST'])
        self.all_chars_luck_boost_label.grid(column=0, row=55, sticky='wns')

        self.all_chars_luck_boost_effect_label = Label(self.win, text="All Luck Boost")
        self.all_chars_luck_boost_effect_label.grid(column=1, row=55, sticky='wns')

        # Hard mode AP multiplier
        self.hardmode_ap_multiplier_label = Label(self.win, text=settings.HOTKEYS['HARDMODE_AP_MULTIPLIER'])
        self.hardmode_ap_multiplier_label.grid(column=0, row=56, sticky='wns')

        self.hardmode_ap_multiplier_effect_label = Label(self.win, text="Hardmode AP Multiplier")
        self.hardmode_ap_multiplier_effect_label.grid(column=1, row=56, sticky='wns')

        # Hard mode EXP multiplier
        self.hardmode_exp_multiplier_label = Label(self.win, text=settings.HOTKEYS['HARDMODE_EXP_MULTIPLIER'])
        self.hardmode_exp_multiplier_label.grid(column=0, row=57, sticky='wns')

        self.hardmode_exp_multiplier_effect_label = Label(self.win, text="Hardmode EXP Multiplier")
        self.hardmode_exp_multiplier_effect_label.grid(column=1, row=57, sticky='wns')

        # Spacer
        self.spacer03 = Label(self.win).grid(column=0, row=59, columnspan=2)

        ### "Add items" menu ###

        self.add_item_label = Label(self.win, text=settings.HOTKEYS['ADD_ITEM'])
        self.add_item_label.grid(column=0, row=62, sticky='wns')

        self.qty_var = StringVar() #For qty_entry
        self.qty_var.set(10)

        self.qty_entry = Entry(
            self.win, 
            textvariable=self.qty_var, 
            font=(settings.Appearance.FONTS['TEXT'], int(settings.Appearance.FONTS['FONT_SIZE'])-1), 
            bg=settings.Appearance.BG_ENTRY, 
            fg=settings.Appearance.FG, 
            bd=0, 
            highlightthickness=0,
            highlightcolor=settings.Appearance.FG, 
            highlightbackground=settings.Appearance.FG, 
            justify='center', 
            width=6,
        )
        self.qty_entry.grid(column=0, row=63, sticky='ens', padx=(0,2))

        self.qty_entry_label = Label(
            self.win, 
            text="Amount:", 
            fg=settings.Appearance.DIM, 
            font=(settings.Appearance.FONTS['TEXT'], int(settings.Appearance.FONTS['FONT_SIZE'])), 
            justify='right',
        ).grid(column=0, row=63, sticky='w')


        self.item_options = Offsets.item_offsets #Note: Configure item_offsets{} dict in offsets.py

        self.selection = StringVar()
        self.selection.set('Choose Item:')


        self.item_menu = OptionMenu(self.win, self.selection, *self.item_options)
        self.item_menu.config(
            bg=settings.Appearance.BG_ENTRY, 
            fg=settings.Appearance.FG, 
            bd=0, 
            activebackground=settings.Appearance.BG_ENTRY, 
            activeforeground=settings.Appearance.FG, 
            font=(settings.Appearance.FONTS['TEXT'], int(settings.Appearance.FONTS['FONT_SIZE'])), 
            padx=0, pady=0, 
            highlightthickness=0, 
            highlightbackground=settings.Appearance.DIM, 
            indicatoron=False,
        )
        # Configure the dropdown
        self.item_menu['menu'].config(
            bg=settings.Appearance.BG,
            fg=settings.Appearance.FG,
            activebackground=settings.Appearance.BLUE, 
            activeforeground=settings.Appearance.BG, 
            font=(settings.Appearance.FONTS['TEXT'], int(settings.Appearance.FONTS['FONT_SIZE'])-1),
            borderwidth=0, 
            border=0, 
            bd=0,
        )
        if settings.Appearance.TRANSPARENT_BG:
            self.item_menu['menu'].config(bg=settings.Appearance.BLACK)
        self.item_menu['menu']['relief'] = 'solid' #flat, groove, raised, ridge, solid, or sunken
        #self.item_menu.config(width = len(max(self.item_options, key=len))) # Width of longest item
        self.item_menu.grid(column=1, row=63, sticky='wens')
        
        #print(self.item_menu.keys())
        #print(self.item_menu['menu'].keys())

        self.button_border_color = Frame(self.win, background=settings.Appearance.BG_ENTRY)
        self.button_border_color.grid(column=1, row=62, sticky='wns', pady=2)

        self.items_submit_button = Button(
            self.button_border_color,
            text='Give Item',
            command=self.get_item_selection,
            borderwidth=0,
            activebackground=settings.Appearance.BG_ENTRY,
            #activebackground=settings.Appearance.BG,
            activeforeground=settings.Appearance.FG,
            bd=0,
        )
        self.items_submit_button.grid(column=1, row=62, sticky='wns', padx=2, pady=2) #padding to show the background Frame

        ### End "add items" menu ###

        # Spacer
        self.spacer04 = Label(self.win)
        self.spacer04.grid(column=0, row=70, columnspan=2)

        # Show trainer info
        self.help_label = Label(self.win, text=settings.HOTKEYS['SHOW_TRAINER_INFO'], foreground=settings.Appearance.DIM)
        self.help_label.grid(column=0, row=90, sticky='wns')

        self.help_effect_label = Label(self.win, text="Help", foreground=settings.Appearance.DIM)
        self.help_effect_label.grid(column=1, row=90, sticky='wns')

        # Show party info
        self.party_info_label = Label(self.win, text=settings.HOTKEYS['SHOW_PARTY_INFO'], foreground=settings.Appearance.DIM)
        self.party_info_label.grid(column=0, row=91, sticky='wns')

        self.party_info_effect_label = Label(self.win, text="Party/game info", foreground=settings.Appearance.DIM)
        self.party_info_effect_label.grid(column=1, row=91, sticky='wns')

        # Toggle window display
        self.open_label = Label(self.win, text=settings.HOTKEYS['HIDE_WINDOW'], foreground=settings.Appearance.DIM)
        self.open_label.grid(column=0, row=92, sticky='wns')

        self.open_effect_label = Label(self.win, text="Show/hide window", foreground=settings.Appearance.DIM)
        self.open_effect_label.grid(column=1, row=92, sticky='wns')

        # Spacer
        self.spacer05 = Label(self.win).grid(column=0, row=100, columnspan=2)

        # Exit button
        self.exit_btn_border = Frame(self.win, background=settings.Appearance.FG)
        self.exit_btn = Button(
            self.exit_btn_border, 
            text=f"Exit ({settings.HOTKEYS['EXIT']})", 
            command=self.win.destroy, 
            bd=0,
        )
        if settings.Appearance.TRANSPARENT_BG:
            # If transparent_bg configured, then use black exit_btn + border frame.
            self.exit_btn.config(bg=settings.Appearance.BLACK)
            self.exit_btn_border.config(background=settings.Appearance.BLACK)

        self.exit_btn_border.grid(column=0, row=120, sticky='wens', columnspan=2)
        self.exit_btn.pack(expand=True, fill='both', padx=1, pady=1)


    def get_item_selection(self) -> None:
        ''' Callback method for "add items" menu submit. '''
        _item_name = self.selection.get()

        # Avoid exception if 'category title' items is selected.
        if _item_name.startswith('--'):
            self.log_error('No item selected!')
            temp_highlight_bg([self.item_menu], settings.Appearance.ERROR, settings.Appearance.BG_ENTRY)
            return None

        # Grab item offset from selected item
        try:
            _offsets = self.item_options[_item_name]
        except (KeyError):
            self.log_error('No item selected!')
            temp_highlight_bg([self.item_menu], settings.Appearance.ERROR, settings.Appearance.BG_ENTRY)
            return None

        # Grab entered quantity
        try:
            _qty: cython.uint = int(self.qty_var.get())
        except ValueError:
            self.log_error('Invalid quantity!')
            temp_highlight_bg([self.qty_entry,], settings.Appearance.ERROR, settings.Appearance.BG_ENTRY)
            return None

        you.give_arbitrary_item(_item_name, _offsets, _qty)
        # Indicate success on GUI label:
        temp_change_property([ct_gui.spacer04], 'text', f'Added {_qty} {_item_name}', '') #Set text contents
        temp_change_property([ct_gui.spacer04], 'foreground', settings.Appearance.ACTIVE, settings.Appearance.FG) #Set FG (text) color

    def toggle_window(self) -> None:
        ''' Toggle show/hide window. '''
        if self.is_hidden == True:
            self.is_hidden = False
            self.win.deiconify()
            self.win.focus_force()
        elif self.is_hidden == False:
            self.is_hidden = True
            self.win.withdraw()

    @staticmethod
    def log_error(_msg: str = 'Invalid input') -> None:
        ''' Display an error in messagebox, and log same message to log handler. 
            Starts a thread to prevent messagebox from blocking highlight methods etc. '''
        logging.error(_msg)
        temp_change_property([ct_gui.spacer04], 'text', _msg, '')

    @staticmethod
    def display_party_info() -> None:
        ''' Display current party member stats in a messagebox. '''
        _msg = 'Current party:\n\n'

        # Append each active party member's stats to _msg.
        for _ in PartyMember.current_party():
            _msg += (
                f'{_.char_name}\n'
                f'HP: {_.current_hp}/{_.max_hp}\n'
                f'MP: {_.current_mp}/{_.max_mp}\n'
                f'ATB: {_.current_atb} / Slots: {_.atb_slots}\n'
                f'Limit: {_.current_limit}\n'
                f'Phy/Mag Atk: {_.atk} / {_.magic_atk}\n'
                f'Phy/Mag Def: {_.defense} / {_.mag_defense}\n'
                f'Luck: {_.luck}\n'
                '\n'
            )

        _msg += (
            f'Controlled char: {you.controlled_character}\n'
            f'Play time: {you.play_time} ({you.play_time // 3600} hrs {(you.play_time % 3600) // 60} mins)\n'
            f'Hard mode: {you.hard_mode}\n'
            f'ATB per slot: {you.atb_per_slot}\n'
            f'ATB rate (player): {you.player_atb_rate}\n'
            f'ATB rate (AI): {you.ai_atb_rate}\n'
            f'Game version: {settings.GAME_VERSION}'
        )

        # Display the text in a messagebox
        messagebox.showinfo('Party info', _msg)

    @staticmethod
    def display_trainer_info() -> None:
        ''' Display trainer info/help in a messagebox. '''
        _hk = 'HOTKEYS:\n'
        for _k, _v in settings.HOTKEYS.items():
            _hk += f'{_k.title().replace("_", " ")}:    {_v.title()}\n'

        _help: cython.unicode = (
            'FF7 Remake Intergrade Trainer by RogueAutomata\n\n'
            'Source code/updates/requests:\n'
            'https://github.com/mepley1/ff7r-trainer\n\n'
            'Appearance + Hotkeys configurable in settings.py\n\n'
            f'{_hk}'
        )

        # Display a messagebox with help text
        messagebox.showinfo('Info', _help)


# Initialize trainer
ct_gui = CheatTrainer("FF7 Remake Trainer")


def main() -> None:
    '''Main.'''

    # Initialize the PartyMember instances AFTER ct_gui, since the labels are a character attribute
    logging.debug('Initializing characters...')
    update_splash('Initializing characters...')

    aerith = PartyMember('Aerith',
        offsets = Offsets.Aerith,
        gui_labels = {
            'godmode': (ct_gui.aerith_godmode_label, ct_gui.aerith_godmode_effect_label),
            'inf_mp': (ct_gui.aerith_inf_mp_label, ct_gui.aerith_inf_mp_effect_label),
            'inf_atb': (ct_gui.aerith_inf_atb_label, ct_gui.aerith_inf_atb_effect_label),
        } if settings.Appearance.ENABLE_INDIVIDUAL_CHARS else {},
    )

    barret = PartyMember('Barret',
        offsets = Offsets.Barret,
        gui_labels = {
            # Barret labels not made yet!
            #'godmode': (ct_gui.barret_godmode_label, ct_gui.barret_godmode_effect_label),
            #'inf_mp': (ct_gui.barret_inf_mp_label, ct_gui.barret_inf_mp_effect_label),
            #'inf_atb': (ct_gui.barret_inf_atb_label, ct_gui.barret_inf_atb_effect_label),
        } if settings.Appearance.ENABLE_INDIVIDUAL_CHARS else {},
    )

    cloud = PartyMember('Cloud',
        offsets = Offsets.Cloud,
        gui_labels = {
            'godmode': (ct_gui.cloud_godmode_label, ct_gui.cloud_godmode_effect_label),
            'inf_mp': (ct_gui.mp_label, ct_gui.mp_effect_label),
            'inf_atb': (ct_gui.cloud_atb_label, ct_gui.atb_effect_label),
            'atk_boost': (ct_gui.cloud_atk_boost_label, ct_gui.cloud_atk_boost_effect_label),
        } if settings.Appearance.ENABLE_INDIVIDUAL_CHARS else {},
    )

    red = PartyMember('Red',
        offsets = Offsets.Red,
        gui_labels = {} if settings.Appearance.ENABLE_INDIVIDUAL_CHARS else {},
    )

    tifa = PartyMember('Tifa',
        offsets = Offsets.Tifa,
        gui_labels = {
            # Tifa labels not made yet!
            #'godmode': (ct_gui.tifa_godmode_label, ct_gui.tifa_godmode_effect_label),
            #'inf_mp': (ct_gui.tifa_inf_mp_label, ct_gui.tifa_inf_mp_effect_label),
            #'inf_atb': (ct_gui.tifa_inf_atb_label, ct_gui.tifa_inf_atb_effect_label),
        } if settings.Appearance.ENABLE_INDIVIDUAL_CHARS else {},
    )

    yuffie = PartyMember('Yuffie',
        offsets = Offsets.Yuffie,
        gui_labels = {
            # yuffie labels not made yet!
            #'godmode': (ct_gui.yuffie_godmode_label, ct_gui.yuffie_godmode_effect_label),
            #'inf_mp': (ct_gui.yuffie_inf_mp_label, ct_gui.yuffie_inf_mp_effect_label),
            #'inf_atb': (ct_gui.yuffie_inf_atb_label, ct_gui.yuffie_inf_atb_effect_label),
        } if settings.Appearance.ENABLE_INDIVIDUAL_CHARS else {},
    )

    sonon = PartyMember('Sonon',
        offsets = Offsets.Sonon,
        gui_labels = {
            # sonon labels not made yet!
            #'godmode': (ct_gui.sonon_godmode_label, ct_gui.sonon_godmode_effect_label),
            #'inf_mp': (ct_gui.sonon_inf_mp_label, ct_gui.sonon_inf_mp_effect_label),
            #'inf_atb': (ct_gui.sonon_inf_atb_label, ct_gui.sonon_inf_atb_effect_label),
        } if settings.Appearance.ENABLE_INDIVIDUAL_CHARS else {},
    )

    ### SET HOTKEYS
    logging.debug('Registering hotkeys...')
    # Cloud
    if settings.Appearance.ENABLE_INDIVIDUAL_CHARS:
        keyboard.add_hotkey(settings.HOTKEYS['CLOUD_GODMODE'], cloud.toggle_godmode)
        keyboard.add_hotkey(settings.HOTKEYS['CLOUD_INF_MP'], cloud.toggle_inf_mp)
        keyboard.add_hotkey(settings.HOTKEYS['CLOUD_INF_ATB'], cloud.toggle_inf_atb)
        keyboard.add_hotkey(settings.HOTKEYS['CLOUD_ATK_BOOST'], cloud.toggle_atk_boost)
    # Aerith
    if settings.Appearance.ENABLE_INDIVIDUAL_CHARS:
        keyboard.add_hotkey(settings.HOTKEYS['AERITH_GODMODE'], aerith.toggle_godmode)
        keyboard.add_hotkey(settings.HOTKEYS['AERITH_INF_MP'], aerith.toggle_inf_mp)
        keyboard.add_hotkey(settings.HOTKEYS['AERITH_INF_ATB'], aerith.toggle_inf_atb)
    # All characters
    keyboard.add_hotkey(settings.HOTKEYS['ALL_CHARS_GODMODE'], PartyMember.all_toggle_godmode)
    keyboard.add_hotkey(settings.HOTKEYS['ALL_CHARS_INF_MP'], PartyMember.all_toggle_inf_mp)
    keyboard.add_hotkey(settings.HOTKEYS['ALL_CHARS_INF_ATB'], PartyMember.all_toggle_inf_atb)
    keyboard.add_hotkey(settings.HOTKEYS['ALL_CHARS_INF_LIMIT'], PartyMember.all_toggle_inf_limit)
    keyboard.add_hotkey(settings.HOTKEYS['ALL_CHARS_ATK_BOOST'], PartyMember.all_toggle_atk_boost)
    keyboard.add_hotkey(settings.HOTKEYS['ALL_CHARS_LUCK_BOOST'], PartyMember.all_toggle_luck_boost)
    # Meta
    keyboard.add_hotkey(settings.HOTKEYS['HARDMODE_AP_MULTIPLIER'], you.toggle_hard_mode_ap_multiplier)
    keyboard.add_hotkey(settings.HOTKEYS['HARDMODE_EXP_MULTIPLIER'], you.toggle_hard_mode_exp_multiplier)
    # Inventory
    keyboard.add_hotkey(settings.HOTKEYS['ADD_ITEM'], ct_gui.get_item_selection)
    # App control
    keyboard.add_hotkey(settings.HOTKEYS['EXIT'], ct_gui.win.destroy)
    keyboard.add_hotkey(settings.HOTKEYS['HIDE_WINDOW'], ct_gui.toggle_window)
    # Info
    keyboard.add_hotkey(settings.HOTKEYS['SHOW_PARTY_INFO'], ct_gui.display_party_info)
    keyboard.add_hotkey(settings.HOTKEYS['SHOW_TRAINER_INFO'], ct_gui.display_trainer_info)

    # Kill the splash screen
    kill_splash()

    # Tkinter main loop (display app window)
    logging.debug('Launching tkinter loop...')
    ct_gui.win.mainloop()

    # Exit 0 after quitting from GUI
    logging.debug('Exiting program.')
    sys.exit(0)

# Mainloop
if __name__ == '__main__':
    main()
