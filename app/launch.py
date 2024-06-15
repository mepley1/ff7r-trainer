''' Launcher/entry point. '''

#Import hooks
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
#App
import gui
import settings #settings.py - App settings
from offsets import Offsets #offsets.py - All offsets

#Entry point
gui.main()
