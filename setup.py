#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='PyTrackDat',
    version='0.2.0',

    python_requires='~=3.6',

    description='A utility for assisting in the creation of online '
                'databases for biological data.',
    url='https://github.com/ColauttiLab/PyTrackDat',
    license='GPLv3',

    author='David Lougheed',
    author_email='david.lougheed@gmail.com',

    packages=find_packages(),
    include_package_data=True,

    entry_points={
        'console_scripts': ['ptd-analyze=pytrackdat.analysis:main',
                            'ptd-generate=pytrackdat.generation:main']
    }
)
