"""
Builds all modules via Cython.
Called by script build_all.bat - Don't run this script manually.
If building manually, use setup.py instead.
"""

from setuptools import setup
from Cython.Build import cythonize

NAME = 'FF7R Trainer'
VERSION = '0.1'
DESC = 'FF7 Remake Cheat Trainer'
URL = 'https://github.com/mepley1/ff7r-trainer'
AUTHOR = 'RogueAutomata'
EMAIL = 'rogueautomata@mepley.net'

SRC_DIR = 'tmp'
PACKAGES = [SRC_DIR]

setup(
    packages=PACKAGES,
    ext_modules=cythonize(
        ['tmp/gui.pyx', 'tmp/settings.pyx', 'tmp/offsets.pyx'],
        compiler_directives={'language_level' : "3"},
        annotate=True,
    ),
    zip_safe=False,
    include_package_data=True,
    name=NAME,
    description=DESC,
    version=VERSION,
    author=AUTHOR,
    author_email=EMAIL,
    url=URL,
)
