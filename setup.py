from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize(
        ['app/gui.py', 'app/settings.py', 'app/offsets.py'],
    ),

)
