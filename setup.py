#!/usr/bin/env python

from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="pytrackdat",
    version="0.3.0",

    python_requires="~=3.6",
    install_requires=["wheel", "virtualenv"],

    description='A utility for assisting in the creation of online '
                'databases for biological data.',
    long_description=long_description,
    long_description_content_type="text/markdown",

    url="https://github.com/pytrackdat/pytrackdat",
    license="GPLv3",
    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent"  # Maybe should be refined
    ],

    author="David Lougheed",
    author_email="david.lougheed@gmail.com",

    packages=["pytrackdat"],
    include_package_data=True,

    entry_points={
        "console_scripts": ["ptd-analyze=pytrackdat.analysis:main",
                            "ptd-generate=pytrackdat.generation:main",
                            "ptd-test=pytrackdat.test_site:main"]
    },

    test_suite="tests"
)
