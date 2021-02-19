#!/usr/bin/env python

from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="pytrackdat",
    version="0.3.0",

    python_requires="~=3.6",
    install_requires=[
        "Django>=2.2.17,<3",
        "django-advanced-filters>=1.2.0,<1.3"
        "django-cors-headers>=3.6.0,<3.7",
        "django-filter>=2.4.0,<2.5",
        "djangorestframework>=3.12.2,<3.13",
        "djangorestframework-simplejwt==4.6.0",
        "django-reversion>=3.0.8,<3.1",
    ],
    extras_require={
        "gis": ["djangorestframework-gis>=0.16.0,<0.17"],
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
        "console_scripts": ["ptd-analyze=pytrackdat.analysis:main",
                            "ptd-generate=pytrackdat.generation:main",
                            "ptd-test=pytrackdat.test_site:main"]
    },

    test_suite="tests"
)
