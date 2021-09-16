================
GIS Data Support
================

macOS:

First, install Python 3 from either Homebrew or the Python website. The default macOS installation **will not work**.

.. code-block:: bash

   brew install sqlite3
   brew install spatialite-tools
   brew install gdal
   SPATIALITE_LIBRARY_PATH=/usr/local/lib/mod_spatialite.dylib PTD_GIS_MODE=true pytrackdat test design_gis.csv
