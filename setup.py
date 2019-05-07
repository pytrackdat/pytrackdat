#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='PyTrackDat',
    version='0.2.0',
    packages=find_packages(),
    entry_points={
        'console_scripts': ['pdt-analyze=pytrackdat.analysis:main',
                            'pdt-generate=pytrackdat.generation:main']
    },

    python_requires='~3.6',

    description='A utility for assisting in the creation of online '
                'databases for biological data.',
    url='https://github.com/ColauttiLab/PyTrackDat',
    license='GPLv3',

    author='David Lougheed',
    author_email='david.lougheed@gmail.com'
)
