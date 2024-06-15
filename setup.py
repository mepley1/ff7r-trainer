"""
(Cython) Build gui module. 
Usage: python setup.py build_ext --inplace
"""

from setuptools import setup
from Cython.Build import cythonize

setup(
    name='FF7R Trainer',
    description='FF7 Remake Trainer',
    ext_modules=cythonize(
        'app/gui.pyx',
        compiler_directives={'language_level' : "3"},
    ),
    #zip_safe=False,
    include_package_data=True,
)
