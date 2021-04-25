# PyTrackDat — A pipeline for online data collection and management

[![PyPI version](https://badge.fury.io/py/pytrackdat.svg)](https://badge.fury.io/py/pytrackdat)
[![Build Status](https://github.com/pytrackdat/pytrackdat/workflows/Tests/badge.svg?branch=master)](https://github.com/pytrackdat/pytrackdat/actions?query=workflow%3ATests+branch%3Amaster)


## Overview

PyTrackDat comprises two Python scripts that analyze and assist in converting
data and relevant metadata from `.csv` files into an online database that can
facilitate data management, manipulation, and quality control. What each of
these scripts does is outlined in this `README.md` file. Note that the care
that is taken to assemble `.csv` files before using these scripts will help
ensure that the database generated is maximally useful.


## Documentation

The latest documentation is available on
[ReadTheDocs](https://pytrackdat.readthedocs.io/en/latest/).


## Notes

### Enabling GIS mode

To enable experimental GIS support, add the following to the shell environment:
```
PTD_GIS=true
```

The `SPATIALITE_LIBRARY_PATH` environment variable must also be configured to 
point to the Spatialite library instance in some cases (if Django cannot find 
it automatically).

#### Using Spatialite for GIS on macOS

To use Spatialite on macOS, it is suggested that `brew` is used to install
the `spatialite-tools` and `gdal` packages.

`SPATIALITE_LIBRARY_PATH` on macOS should be the following:

```
SPATIALITE_LIBRARY_PATH='/usr/local/lib/mod_spatialite.dylib'
```

The built-in `python3` that ships with macOS does not have extension support
enabled, and thus cannot be used to build the PyTrackDat site.
