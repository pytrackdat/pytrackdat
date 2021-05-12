#!/usr/bin/env python

from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="pytrackdat",
    version="0.3.0",

    python_requires="~=3.7",
    install_requires=[
        "Django>=3.2.2,<3.3",
        "django-advanced-filters>=1.3.0,<1.4",
        "django-cors-headers>=3.7.0,<3.8",
        "django-filter>=2.4.0,<2.5",
        "djangorestframework>=3.12.4,<3.13",
        "djangorestframework-simplejwt==4.6.0",
        "django-reversion>=3.0.9,<3.1",
    ],
    extras_require={
        "gis": ["djangorestframework-gis>=0.17.0,<0.18"],
    },

    description="A utility for assisting in the creation of online "
                "databases for biological data.",
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
        "console_scripts": ["pytrackdat=pytrackdat.entry:main"],
    },

    test_suite="tests"
)
